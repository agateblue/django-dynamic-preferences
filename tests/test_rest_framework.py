from __future__ import unicode_literals
import json

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import caches

from dynamic_preferences.registries import global_preferences_registry as registry
from dynamic_preferences.users.registries import (
    user_preferences_registry as user_registry,
)
from dynamic_preferences.api import serializers
from dynamic_preferences.users.serializers import UserPreferenceSerializer


def test_can_serialize_preference(db):
    manager = registry.manager()
    pref = manager.get_db_pref(section="user", name="max_users")

    serializer = serializers.GlobalPreferenceSerializer(pref)
    data = serializer.data

    assert data["default"] == pref.preference.api_repr(pref.preference.default)
    assert data["value"] == pref.preference.api_repr(pref.value)
    assert data["identifier"] == pref.preference.identifier()
    assert data["section"] == pref.section
    assert data["name"] == pref.name
    assert data["verbose_name"] == pref.preference.verbose_name
    assert data["help_text"] == pref.preference.help_text
    assert data["field"]["class"] == "IntegerField"
    assert data["field"]["input_type"] == "number"
    assert data["field"]["widget"]["class"] == "NumberInput"

    pref = manager.get_db_pref(section="exam", name="duration")
    serializer = serializers.GlobalPreferenceSerializer(pref)
    data = serializer.data
    assert data["value"] == "03:00:00"

    pref = manager.get_db_pref(section="company", name="RegistrationDate")
    serializer = serializers.GlobalPreferenceSerializer(pref)
    data = serializer.data
    assert data["value"] == "1998-09-04"

    pref = manager.get_db_pref(section="child", name="BirthDateTime")
    serializer = serializers.GlobalPreferenceSerializer(pref)
    data = serializer.data
    assert data["value"] == "1992-05-04T03:04:10.000150+00:00"


def test_can_change_preference_value_using_serializer(db):
    manager = registry.manager()
    pref = manager.get_db_pref(section="user", name="max_users")
    data = {"value": 666}
    serializer = serializers.GlobalPreferenceSerializer(pref, data=data)

    is_valid = serializer.is_valid()
    assert is_valid is True

    serializer.save()
    pref = manager.get_db_pref(section="user", name="max_users")

    assert pref.value == data["value"]


def test_serializer_also_uses_custom_clean_method(db):
    manager = registry.manager()
    pref = manager.get_db_pref(section="user", name="max_users")

    # will fail because of preference cleaning
    data = {"value": 1001}
    serializer = serializers.GlobalPreferenceSerializer(pref, data=data)

    is_valid = serializer.is_valid()
    assert is_valid is False
    assert "value" in serializer.errors


def test_serializer_includes_additional_data_if_any(fake_user):
    manager = user_registry.manager(instance=fake_user)
    pref = manager.get_db_pref(section="user", name="favorite_vegetable")

    serializer = UserPreferenceSerializer(pref)
    assert serializer.data["additional_data"]["choices"] == pref.preference.choices


def test_global_preference_list_requires_permission(db, client):
    url = reverse("api:global-list")

    # anonymous
    response = client.get(url)
    assert response.status_code == 403

    client.login(username="test", password="test")

    response = client.get(url)
    assert response.status_code == 403


def test_can_list_preferences(admin_client):
    manager = registry.manager()
    url = reverse("api:global-list")
    response = admin_client.get(url)
    assert response.status_code == 200

    payload = json.loads(response.content.decode("utf-8"))

    assert len(payload) == len(registry.preferences())

    for e in payload:
        pref = manager.get_db_pref(section=e["section"], name=e["name"])
        serializer = serializers.GlobalPreferenceSerializer(pref)
        assert pref.preference.identifier() == e["identifier"]


def test_can_list_preferences_with_section_filter(admin_client):
    manager = registry.manager()
    url = reverse("api:global-list")
    response = admin_client.get(url, {"section": "user"})
    assert response.status_code == 200

    payload = json.loads(response.content.decode("utf-8"))

    assert len(payload) == len(registry.preferences("user"))

    for e in payload:
        pref = manager.get_db_pref(section=e["section"], name=e["name"])
        serializers.GlobalPreferenceSerializer(pref)
        assert pref.preference.identifier() == e["identifier"]


def test_can_detail_preference(admin_client):
    manager = registry.manager()
    pref = manager.get_db_pref(section="user", name="max_users")
    url = reverse("api:global-detail", kwargs={"pk": pref.preference.identifier()})
    response = admin_client.get(url)
    assert response.status_code == 200

    payload = json.loads(response.content.decode("utf-8"))
    assert pref.preference.identifier(), payload["identifier"]
    assert pref.value == payload["value"]


def test_can_update_preference(admin_client):
    manager = registry.manager()
    pref = manager.get_db_pref(section="user", name="max_users")
    url = reverse("api:global-detail", kwargs={"pk": pref.preference.identifier()})
    response = admin_client.patch(
        url, json.dumps({"value": 16}), content_type="application/json"
    )
    assert response.status_code == 200

    pref = manager.get_db_pref(section="user", name="max_users")

    assert pref.value == 16


def test_can_update_decimal_preference(admin_client):
    manager = registry.manager()
    pref = manager.get_db_pref(section="type", name="cost")
    url = reverse("api:global-detail", kwargs={"pk": pref.preference.identifier()})
    response = admin_client.patch(
        url, json.dumps({"value": "111.11"}), content_type="application/json"
    )
    assert response.status_code == 200

    pref = manager.get_db_pref(section="type", name="cost")

    assert pref.value == Decimal("111.11")


def test_can_update_multiple_preferences(admin_client):
    manager = registry.manager()
    pref = manager.get_db_pref(section="user", name="max_users")
    url = reverse("api:global-bulk")

    payload = {
        "user__max_users": 16,
        "user__registration_allowed": True,
    }
    response = admin_client.post(
        url, json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 200

    pref1 = manager.get_db_pref(section="user", name="max_users")
    pref2 = manager.get_db_pref(section="user", name="registration_allowed")

    assert pref1.value == 16
    assert pref2.value == True


def test_update_preference_returns_validation_error(admin_client):
    manager = registry.manager()
    pref = manager.get_db_pref(section="user", name="max_users")
    url = reverse("api:global-detail", kwargs={"pk": pref.preference.identifier()})
    response = admin_client.patch(
        url, json.dumps({"value": 1001}), content_type="application/json"
    )
    assert response.status_code == 400

    payload = json.loads(response.content.decode("utf-8"))

    assert payload["value"] == ["Wrong value!"]


def test_update_multiple_preferences_with_validation_errors_rollback(admin_client):
    manager = registry.manager()
    pref = manager.get_db_pref(section="user", name="max_users")
    url = reverse("api:global-bulk")
    payload = {
        "user__max_users": 1001,
        "user__registration_allowed": True,
    }
    response = admin_client.post(
        url, json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 400

    errors = json.loads(response.content.decode("utf-8"))
    assert errors[pref.preference.identifier()]["value"] == ["Wrong value!"]

    pref1 = manager.get_db_pref(section="user", name="max_users")
    pref2 = manager.get_db_pref(section="user", name="registration_allowed")

    assert pref1.value == pref1.preference.default
    assert pref2.value == pref2.preference.default
