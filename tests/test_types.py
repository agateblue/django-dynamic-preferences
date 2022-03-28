import os
import decimal
import pytest

from datetime import date, timedelta, datetime, time
from django import forms
from django.test import TestCase
from django.db.models import signals
from django.test.utils import override_settings
from django.core.cache import caches
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth.models import User

from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.settings import preferences_settings
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences import types

from .test_app.models import BlogEntry


@pytest.fixture
def no_validate_names(settings):
    settings.DYNAMIC_PREFERENCES = {"VALIDATE_NAMES": False}


@pytest.fixture
def blog_entry(db):
    return BlogEntry.objects.create(title="Hello", content="World")


def test_default_accepts_callable(no_validate_names):
    class P(types.IntPreference):
        def get_default(self):
            return 4

    assert P().get("default") == 4


def test_getter(no_validate_names):
    class PNoGetter(types.IntPreference):
        default = 1
        help_text = "Hello"

    class PGetter(types.IntPreference):
        def get_default(self):
            return 1

        def get_help_text(self):
            return "Hello"

    p_no_getter = PNoGetter()
    p_getter = PGetter()
    for attribute, expected in [("default", 1), ("help_text", "Hello")]:
        assert p_no_getter.get(attribute) == expected
        assert p_getter.get(attribute) == expected


def test_field(no_validate_names):
    class P(types.IntPreference):
        default = 1
        verbose_name = "P"

    p = P()

    assert p.field.initial == 1
    assert p.field.label == "P"
    assert p.field.__class__ == forms.IntegerField


def test_boolean_field_class_instantiation(no_validate_names):
    class P(types.BooleanPreference):
        default = False

    preference = P()
    assert preference.field.initial == False


def test_char_field_class_instantiation(no_validate_names):
    class P(types.StringPreference):
        default = "hello world!"

    preference = P()

    assert preference.field.initial == "hello world!"


def test_longstring_preference_widget(no_validate_names):
    class P(types.LongStringPreference):
        default = "hello world!"

    preference = P()

    assert isinstance(preference.field.widget, forms.Textarea) is True


def test_decimal_preference(no_validate_names):
    class P(types.DecimalPreference):
        default = decimal.Decimal("2.5")

    preference = P()

    assert preference.field.initial == decimal.Decimal("2.5")


def test_float_preference(no_validate_names):
    class P(types.FloatPreference):
        default = 0.35

    preference = P()

    assert preference.field.initial == 0.35
    assert preference.field.initial != 0.3
    assert preference.field.initial != 0.3001


def test_duration_preference(no_validate_names):
    class P(types.DurationPreference):
        default = timedelta(0)

    preference = P()

    assert preference.field.initial == timedelta(0)


def test_date_preference(no_validate_names):
    class P(types.DatePreference):
        default = date.today()

    preference = P()

    assert preference.field.initial == date.today()


def test_datetime_preference(no_validate_names):
    initial_date_time = datetime(2017, 10, 4, 23, 7, 20, 682380)

    class P(types.DateTimePreference):
        default = initial_date_time

    preference = P()

    assert preference.field.initial == initial_date_time


def test_time_preference(no_validate_names):
    class P(types.TimePreference):
        default = time(0)

    preference = P()

    assert preference.field.initial == time(0)


def test_file_preference_defaults_to_none(no_validate_names):
    class P(types.FilePreference):
        pass

    preference = P()

    assert preference.field.initial is None


def test_can_get_upload_path(no_validate_names):
    class P(types.FilePreference):
        pass

    p = P()

    assert p.get_upload_path() == (
        preferences_settings.FILE_PREFERENCE_UPLOAD_DIR + "/" + p.identifier()
    )


def test_file_preference_store_file_path(db):
    f = SimpleUploadedFile(
        "test_file_1ce410e5-6814-4910-afd7-be1486d3644f.txt",
        "hello world".encode("utf-8"),
    )
    p = global_preferences_registry.get(section="blog", name="logo")
    manager = global_preferences_registry.manager()
    manager["blog__logo"] = f
    assert manager["blog__logo"].read() == b"hello world"
    assert manager["blog__logo"].url == os.path.join(
        settings.MEDIA_URL, p.get_upload_path(), f.name
    )

    assert manager["blog__logo"].path == os.path.join(
        settings.MEDIA_ROOT, p.get_upload_path(), f.name
    )


def test_file_preference_conflicting_file_names(db):
    """
    f2 should have a different file name to f, since Django storage needs
    to differentiate between the two
    """
    f = SimpleUploadedFile(
        "test_file_c95d02ef-0e5d-4d36-98c0-1b54505860d0.txt",
        "hello world".encode("utf-8"),
    )
    f2 = SimpleUploadedFile(
        "test_file_c95d02ef-0e5d-4d36-98c0-1b54505860d0.txt",
        "hello world 2".encode("utf-8"),
    )
    p = global_preferences_registry.get(section="blog", name="logo")
    manager = global_preferences_registry.manager()

    manager["blog__logo"] = f
    manager["blog__logo2"] = f2

    assert manager["blog__logo2"].read() == b"hello world 2"
    assert manager["blog__logo"].read() == b"hello world"

    assert manager["blog__logo"].url != manager["blog__logo2"].url
    assert manager["blog__logo"].path != manager["blog__logo2"].path


def test_can_delete_file_preference(db):
    f = SimpleUploadedFile(
        "test_file_bf2e72ef-092f-4a71-9cda-f2442d6166d0.txt",
        "hello world".encode("utf-8"),
    )
    p = global_preferences_registry.get(section="blog", name="logo")
    manager = global_preferences_registry.manager()
    manager["blog__logo"] = f
    path = os.path.join(settings.MEDIA_ROOT, p.get_upload_path(), f.name)
    assert os.path.exists(path) is True
    manager["blog__logo"].delete()
    assert os.path.exists(path) is False


def test_file_preference_api_repr_returns_path(db):
    f = SimpleUploadedFile(
        "test_file_24485a80-8db9-4191-ae49-da7fe2013794.txt",
        "hello world".encode("utf-8"),
    )
    p = global_preferences_registry.get(section="blog", name="logo")
    manager = global_preferences_registry.manager()
    manager["blog__logo"] = f

    f = manager["blog__logo"]
    assert p.api_repr(f) == f.url


def test_choice_preference(fake_user):
    fake_user.preferences["user__favorite_vegetable"] = "C"
    assert fake_user.preferences["user__favorite_vegetable"] == "C"
    fake_user.preferences["user__favorite_vegetable"] = "P"
    assert fake_user.preferences["user__favorite_vegetable"] == "P"

    with pytest.raises(forms.ValidationError):
        fake_user.preferences["user__favorite_vegetable"] = "Nope"


def test_multiple_choice_preference(fake_user):
    fake_user.preferences["user__favorite_vegetables"] = ["C", "T"]
    assert fake_user.preferences["user__favorite_vegetables"] == ["C", "T"]
    fake_user.preferences["user__favorite_vegetables"] = ["P"]
    assert fake_user.preferences["user__favorite_vegetables"] == ["P"]

    with pytest.raises(forms.ValidationError):
        fake_user.preferences["user__favorite_vegetables"] = ["Nope", "C"]


def test_model_choice_preference(blog_entry):
    global_preferences = global_preferences_registry.manager()
    global_preferences["blog__featured_entry"] = blog_entry

    in_db = GlobalPreferenceModel.objects.get(section="blog", name="featured_entry")
    assert in_db.value == blog_entry
    assert in_db.raw_value == str(blog_entry.pk)


def test_deleting_model_also_delete_preference(blog_entry):
    global_preferences = global_preferences_registry.manager()
    global_preferences["blog__featured_entry"] = blog_entry

    assert len(signals.pre_delete.receivers) > 0

    blog_entry.delete()

    with pytest.raises(GlobalPreferenceModel.DoesNotExist):
        GlobalPreferenceModel.objects.get(section="blog", name="featured_entry")
