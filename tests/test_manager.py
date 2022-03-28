from __future__ import unicode_literals
from django.test import TestCase
from django.core.cache import caches
from django.urls import reverse
from django.contrib.auth.models import User

from dynamic_preferences.registries import global_preferences_registry as registry
from dynamic_preferences.models import GlobalPreferenceModel


def test_can_get_preferences_objects_from_manager(db):
    manager = registry.manager()
    cached_prefs = dict(manager.all())
    qs = manager.queryset

    assert len(qs) == len(cached_prefs)

    assert list(qs) == list(GlobalPreferenceModel.objects.all())


def test_can_get_db_pref_from_manager(db):
    manager = registry.manager()
    manager.queryset.delete()
    pref = manager.get_db_pref(section="test", name="TestGlobal1")

    assert pref.section == "test"
    assert pref.name == "TestGlobal1"
    assert pref.raw_value == registry.get("test__TestGlobal1").default


def test_do_not_restore_default_when_calling_all(db, cache):
    manager = registry.manager()

    new_value = "test_new_value"
    manager["test__TestGlobal1"] = new_value
    assert manager["test__TestGlobal1"] == new_value
    cache.clear()
    manager.all()
    cache.clear()
    assert manager["test__TestGlobal1"] == new_value
    assert manager.all()["test__TestGlobal1"] == new_value


def test_invalidates_cache_when_saving_database_preference(db, cache):
    manager = registry.manager()
    cache.clear()
    new_value = "test_new_value"
    key = manager.get_cache_key("test", "TestGlobal1")
    manager["test__TestGlobal1"] = new_value

    pref = manager.get_db_pref(section="test", name="TestGlobal1")
    assert pref.raw_value == new_value
    assert manager.cache.get(key) == new_value

    pref.raw_value = "reset"
    pref.save()

    assert manager.cache.get(key) == "reset"


def test_invalidates_cache_when_saving_from_admin(admin_client):

    manager = registry.manager()
    pref = manager.get_db_pref(section="test", name="TestGlobal1")
    url = reverse(
        "admin:dynamic_preferences_globalpreferencemodel_change", args=(pref.id,)
    )
    key = manager.get_cache_key("test", "TestGlobal1")

    response = admin_client.post(url, {"raw_value": "reset1"})

    assert manager.cache.get(key) == "reset1"
    assert manager.all()["test__TestGlobal1"] == "reset1"

    response = admin_client.post(url, {"raw_value": "reset2"})

    assert manager.cache.get(key) == "reset2"
    assert manager.all()["test__TestGlobal1"] == "reset2"
