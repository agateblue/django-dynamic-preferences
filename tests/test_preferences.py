from __future__ import unicode_literals
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.core.cache import caches

import pytest

from dynamic_preferences.registries import (
    MissingPreference,
    global_preferences_registry,
)
from dynamic_preferences import preferences, exceptions
from dynamic_preferences.types import IntegerPreference, StringPreference
from dynamic_preferences.signals import preference_updated

from .test_app import dynamic_preferences_registry as prefs
from .test_app.models import BlogEntry

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


def test_can_retrieve_preference_using_dotted_notation(db):
    registration_allowed = global_preferences_registry.get(
        name="registration_allowed", section="user"
    )
    dotted_result = global_preferences_registry.get("user__registration_allowed")
    assert registration_allowed == dotted_result


def test_can_register_and_retrieve_preference_with_section_none(db):
    no_section_pref = global_preferences_registry.get(name="no_section")
    assert no_section_pref.section == preferences.EMPTY_SECTION


def test_cannot_instanciate_preference_or_section_with_invalid_name():

    invalid_names = ["with space", "with__separator", "with-hyphen"]

    for n in invalid_names:
        with pytest.raises(ValueError):
            preferences.Section(n)
        with pytest.raises(ValueError):

            class P(IntegerPreference):
                name = n

            P()


def test_preference_order_match_register_call():
    expected = [
        "registration_allowed",
        "max_users",
        "items_per_page",
        "featured_entry",
    ]
    assert [p.name for p in global_preferences_registry.preferences()][:4] == expected


def test_preferences_manager_get(db):
    global_preferences = global_preferences_registry.manager()
    assert global_preferences["no_section"] is False


def test_preferences_manager_set(db):
    global_preferences = global_preferences_registry.manager()
    global_preferences["no_section"] = True
    assert global_preferences["no_section"] is True


def test_can_cache_single_preference(db, django_assert_num_queries):

    manager = global_preferences_registry.manager()
    v = manager["no_section"]
    with django_assert_num_queries(0):
        v = manager["no_section"]
        v = manager["no_section"]
        v = manager["no_section"]


def test_can_bypass_cache_in_get(db, settings, django_assert_num_queries):
    settings.DYNAMIC_PREFERENCES = {"ENABLE_CACHE": False}
    manager = global_preferences_registry.manager()
    manager["no_section"]
    with django_assert_num_queries(3):
        manager["no_section"]
        manager["no_section"]
        manager["no_section"]


def test_can_bypass_cache_in_get_all(db, settings):
    settings.DYNAMIC_PREFERENCES = {"ENABLE_CACHE": False}
    settings.DEBUG = True
    from django.db import connection

    manager = global_preferences_registry.manager()

    queries_before = len(connection.queries)
    manager.all()
    manager_queries = len(connection.queries) - queries_before

    manager.all()
    assert len(connection.queries) > manager_queries


def test_can_cache_all_preferences(db, django_assert_num_queries):
    blog_entry = BlogEntry.objects.create(title="test", content="test")
    manager = global_preferences_registry.manager()
    manager.all()
    with django_assert_num_queries(3):
        # one request each time we retrieve the blog entry
        manager.all()
        manager.all()
        manager.all()


def test_preferences_manager_by_name(db):
    manager = global_preferences_registry.manager()
    assert manager.by_name()["max_users"] == manager["user__max_users"]
    assert len(manager.all()) == len(manager.by_name())


def test_cache_invalidate_on_save(db, django_assert_num_queries):
    manager = global_preferences_registry.manager()
    model_instance = manager.create_db_pref(
        section=None, name="no_section", value=False
    )

    with django_assert_num_queries(0):
        assert not manager["no_section"]
        manager["no_section"]

    model_instance.value = True
    model_instance.save()

    with django_assert_num_queries(0):
        assert manager["no_section"]
        manager["no_section"]


def test_can_get_single_pref_with_cache_disabled(settings, db):
    settings.DYNAMIC_PREFERENCES = {"ENABLE_CACHE": False}
    manager = global_preferences_registry.manager()
    v = manager["no_section"]
    assert isinstance(v, bool) is True


def test_can_get_single_pref_bypassing_cache(db):
    manager = global_preferences_registry.manager()
    v = manager.get("no_section", no_cache=True)
    assert isinstance(v, bool) is True


def test_do_not_crash_if_preference_is_missing_in_registry(db):
    """see #41"""
    manager = global_preferences_registry.manager()
    instance = manager.create_db_pref(section=None, name="bad_pref", value="something")

    assert isinstance(instance.preference, MissingPreference) is True

    assert instance.preference.section is None
    assert instance.preference.name == "bad_pref"
    assert instance.value == "something"


def test_can_get_to_string_notation(db):
    pref = global_preferences_registry.get("user__registration_allowed")

    assert pref.identifier() == "user__registration_allowed"


def test_preference_requires_default_value():
    with pytest.raises(exceptions.MissingDefault):
        preference = prefs.NoDefault()


def test_modelchoicepreference_requires_model_value():
    with pytest.raises(exceptions.MissingModel):
        preference = prefs.NoModel()


def test_get_field_uses_field_kwargs():
    class P(StringPreference):
        name = "test"
        default = ""
        field_kwargs = {"required": False}

    p = P()

    kwargs = p.get_field_kwargs()
    assert kwargs["required"] is False


def test_preferences_manager_signal(db):
    global_preferences = global_preferences_registry.manager()
    global_preferences["no_section"] = False
    receiver = MagicMock()
    preference_updated.connect(receiver)
    global_preferences["no_section"] = True
    assert receiver.call_count == 1
    call_args = receiver.call_args[1]
    assert {
        "sender": global_preferences.__class__,
        "section": None,
        "name": "no_section",
        "old_value": False,
        "new_value": True,
    }.items() <= call_args.items()
