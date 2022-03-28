from __future__ import unicode_literals

import pytest


from datetime import timezone
from decimal import Decimal

from datetime import date, timedelta, datetime, time
from django.apps import apps
from django.test import LiveServerTestCase, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.core.management import call_command
from django.core.cache import caches
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.timezone import make_aware

from dynamic_preferences.registries import global_preferences_registry as registry
from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.forms import global_preference_form_builder

from .test_app.models import BlogEntry


def test_preference_model_manager_to_dict(db):
    manager = registry.manager()
    call_command("checkpreferences", verbosity=1)
    expected = {
        "test__TestGlobal1": "default value",
        "test__TestGlobal2": False,
        "test__TestGlobal3": False,
        "type__cost": Decimal(0),
        "exam__duration": timedelta(hours=3),
        "no_section": False,
        "user__max_users": 100,
        "user__items_per_page": 25,
        "blog__featured_entry": None,
        "blog__logo": None,
        "blog__logo2": None,
        "company__RegistrationDate": date(1998, 9, 4),
        "child__BirthDateTime": datetime(
            1992, 5, 4, 3, 4, 10, 150, tzinfo=timezone.utc
        ),
        "company__OpenningTime": time(hour=8, minute=0),
        "user__registration_allowed": False,
    }

    assert manager.all() == expected


def test_registry_default_preference_model(settings):
    app_config = apps.app_configs["dynamic_preferences"]
    registry.preference_model = None

    settings.DYNAMIC_PREFERENCES = {"ENABLE_GLOBAL_MODEL_AUTO_REGISTRATION": False}

    app_config.ready()

    assert registry.preference_model is None

    settings.DYNAMIC_PREFERENCES = {"ENABLE_GLOBAL_MODEL_AUTO_REGISTRATION": True}

    app_config.ready()

    assert registry.preference_model is GlobalPreferenceModel


def test_can_build_global_preference_form(db):
    # We want to display a form with two global preferences
    # RegistrationAllowed and MaxUsers
    form = global_preference_form_builder(
        preferences=["user__registration_allowed", "user__max_users"]
    )()

    assert len(form.fields) == 2
    assert form.fields["user__registration_allowed"].initial is False


def test_can_build_preference_form_from_sections(db):
    form = global_preference_form_builder(section="test")()

    assert len(form.fields) == 3


def test_can_build_global_preference_form_from_sections(db):
    form = global_preference_form_builder(section="test")()

    assert len(form.fields) == 3


def test_global_preference_view_requires_staff_member(
    fake_admin, assert_redirect, client
):
    url = reverse("dynamic_preferences:global")
    response = client.get(url)

    assert_redirect(response, "/admin/login/?next=/global/")

    client.login(username="henri", password="test")
    response = client.get(url)
    assert_redirect(response, "/admin/login/?next=/global/")

    client.login(username="admin", password="test")
    response = client.get(url)

    assert fake_admin.is_authenticated is True
    assert response.status_code == 200


def test_global_preference_view_display_form(admin_client):

    url = reverse("dynamic_preferences:global")
    response = admin_client.get(url)
    assert len(response.context["form"].fields) == 15
    assert response.context["registry"] == registry


def test_global_preference_view_section_verbose_names(admin_client):
    url = reverse("admin:dynamic_preferences_globalpreferencemodel_changelist")
    response = admin_client.get(url)
    for key, section in registry.section_objects.items():
        if section.name != section.verbose_name:
            # Assert verbose_name in table
            assert str(response._container).count(section.verbose_name + "</td>") >= 1
            # Assert verbose_name in filter link
            assert str(response._container).count(section.verbose_name + "</a>") >= 1


def test_formview_includes_section_in_context(admin_client):
    url = reverse("dynamic_preferences:global.section", kwargs={"section": "user"})
    response = admin_client.get(url)
    assert response.context["section"] == registry.section_objects["user"]


def test_formview_with_bad_section_returns_404(admin_client):
    url = reverse("dynamic_preferences:global.section", kwargs={"section": "nope"})
    response = admin_client.get(url)
    assert response.status_code == 404


def test_global_preference_filters_by_section(admin_client):
    url = reverse("dynamic_preferences:global.section", kwargs={"section": "user"})
    response = admin_client.get(url)
    assert len(response.context["form"].fields) == 3


def test_preference_are_updated_on_form_submission(admin_client):
    blog_entry = BlogEntry.objects.create(title="test", content="test")
    url = reverse("dynamic_preferences:global")
    data = {
        "user__max_users": 67,
        "user__registration_allowed": True,
        "user__items_per_page": 12,
        "test__TestGlobal1": "new value",
        "test__TestGlobal2": True,
        "test__TestGlobal3": True,
        "no_section": True,
        "blog__featured_entry": blog_entry.pk,
        "company__RegistrationDate": date(1976, 4, 1),
        "child__BirthDateTime": datetime.now(),
        "type__cost": 1,
        "exam__duration": timedelta(hours=5),
        "company__OpenningTime": time(hour=8, minute=0),
    }
    response = admin_client.post(url, data)
    for key, expected_value in data.items():
        try:
            section, name = key.split("__")
        except ValueError:
            section, name = (None, key)

        p = GlobalPreferenceModel.objects.get(name=name, section=section)
        if name == "featured_entry":
            expected_value = blog_entry
        if name == "BirthDateTime":
            expected_value = make_aware(expected_value)

        assert p.value == expected_value


def test_preference_are_updated_on_form_submission_by_section(admin_client):
    url = reverse("dynamic_preferences:global.section", kwargs={"section": "user"})
    response = admin_client.post(
        url,
        {
            "user__max_users": 95,
            "user__registration_allowed": True,
            "user__items_per_page": 12,
        },
    )
    assert (
        GlobalPreferenceModel.objects.get(section="user", name="max_users").value == 95
    )
    assert (
        GlobalPreferenceModel.objects.get(
            section="user", name="registration_allowed"
        ).value
        is True
    )
    assert (
        GlobalPreferenceModel.objects.get(section="user", name="items_per_page").value
        == 12
    )


def test_template_gets_global_preferences_via_template_processor(db, client):
    global_preferences = registry.manager()
    url = reverse("dynamic_preferences.test.templateview")
    response = client.get(url)
    assert response.context["global_preferences"] == global_preferences.all()


def test_file_preference(admin_client):
    blog_entry = BlogEntry.objects.create(title="Hello", content="World")
    content = b"hello"
    logo = SimpleUploadedFile("logo.png", content, content_type="image/png")
    url = reverse("dynamic_preferences:global.section", kwargs={"section": "blog"})
    response = admin_client.post(
        url, {"blog__featured_entry": blog_entry.pk, "blog__logo": logo}
    )
    assert (
        GlobalPreferenceModel.objects.get(section="blog", name="featured_entry").value
        == blog_entry
    )
    assert (
        GlobalPreferenceModel.objects.get(section="blog", name="logo").value.read()
        == content
    )
