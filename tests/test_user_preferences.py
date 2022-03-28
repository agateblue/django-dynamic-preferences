from __future__ import unicode_literals
import json
import pytest

from django.test import LiveServerTestCase, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import caches
from django.db import IntegrityError

from dynamic_preferences.users.registries import user_preferences_registry as registry
from dynamic_preferences.users.models import UserPreferenceModel
from dynamic_preferences.users import serializers
from dynamic_preferences.managers import PreferencesManager
from dynamic_preferences.users.forms import user_preference_form_builder


def test_adding_user_create_default_preferences(db):

    u = User.objects.create(username="post_create")

    assert len(u.preferences) == len(registry.preferences())


def test_manager_is_attached_to_each_referenced_instance(fake_user):
    assert isinstance(fake_user.preferences, PreferencesManager) is True


def test_preference_is_saved_to_database(fake_user):

    fake_user.preferences["test__TestUserPref1"] = "new test value"

    test_user_pref1 = UserPreferenceModel.objects.get(
        section="test", name="TestUserPref1", instance=fake_user
    )

    assert fake_user.preferences["test__TestUserPref1"] == "new test value"


def test_per_instance_preference_stay_unique_in_db(fake_user):

    fake_user.preferences["test__TestUserPref1"] = "new value"

    duplicate = UserPreferenceModel(
        section="test", name="TestUserPref1", instance=fake_user
    )

    with pytest.raises(IntegrityError):
        duplicate.save()


def test_preference_value_set_to_default(fake_user):

    pref = registry.get("TestUserPref1", "test")

    value = fake_user.preferences["test__TestUserPref1"]
    assert pref.default == value
    instance = UserPreferenceModel.objects.get(
        section="test", name="TestUserPref1", instance=fake_user
    )


def test_user_preference_model_manager_to_dict(fake_user):
    expected = {
        "misc__favourite_colour": "Green",
        "misc__is_zombie": True,
        "user__favorite_vegetable": "C",
        "user__favorite_vegetables": ["C", "P"],
        "test__SUserStringPref": "Hello world!",
        "test__SiteBooleanPref": False,
        "test__TestUserPref1": "default value",
        "test__TestUserPref2": "default value",
    }
    assert fake_user.preferences.all() == expected


def test_can_build_user_preference_form_from_sections(fake_admin):
    form = user_preference_form_builder(instance=fake_admin, section="test")()

    assert len(form.fields) == 4


def test_user_preference_form_is_bound_with_current_user(henri_client, henri):
    assert (
        UserPreferenceModel.objects.get_or_create(
            instance=henri, section="misc", name="favourite_colour"
        )[0].value
        == "Green"
    )
    assert (
        UserPreferenceModel.objects.get_or_create(
            instance=henri, section="misc", name="is_zombie"
        )[0].value
        is True
    )

    url = reverse("dynamic_preferences:user.section", kwargs={"section": "misc"})
    response = henri_client.post(
        url, {"misc__favourite_colour": "Purple", "misc__is_zombie": False}, follow=True
    )
    assert response.status_code == 200
    assert henri.preferences["misc__favourite_colour"] == "Purple"
    assert henri.preferences["misc__is_zombie"] is False


def test_preference_list_requires_authentication(client):
    url = reverse("api:user-list")

    # anonymous
    response = client.get(url)
    assert response.status_code == 403


def test_can_list_preferences(user_client, fake_user):
    manager = registry.manager(instance=fake_user)
    url = reverse("api:user-list")

    response = user_client.get(url)
    assert response.status_code == 200

    payload = json.loads(response.content.decode("utf-8"))

    assert len(payload) == len(registry.preferences())

    for e in payload:
        pref = manager.get_db_pref(section=e["section"], name=e["name"])
        serializer = serializers.UserPreferenceSerializer(pref)
        assert pref.preference.identifier() == e["identifier"]


def test_can_list_preference_of_requesting_user(fake_user, user_client):
    second_user = User(
        username="user2", email="user2@user.com", is_superuser=True, is_staff=True
    )
    second_user.set_password("test")
    second_user.save()

    manager = registry.manager(instance=fake_user)
    url = reverse("api:user-list")
    response = user_client.get(url)
    assert response.status_code == 200

    payload = json.loads(response.content.decode("utf-8"))

    assert len(payload) == len(registry.preferences())

    url = reverse("api:user-list")
    user_client.login(username="user2", password="test")
    response = user_client.get(url)
    assert response.status_code == 200

    payload = json.loads(response.content.decode("utf-8"))

    # This should be 7 because each user gets 7 preferences by default.
    assert len(payload) == 8

    for e in payload:
        pref = manager.get_db_pref(section=e["section"], name=e["name"])
        serializer = serializers.UserPreferenceSerializer(pref)
        assert pref.preference.identifier() == e["identifier"]


def test_can_detail_preference(fake_user, user_client):
    manager = registry.manager(instance=fake_user)
    pref = manager.get_db_pref(section="user", name="favorite_vegetable")
    url = reverse("api:user-detail", kwargs={"pk": pref.preference.identifier()})
    response = user_client.get(url)
    assert response.status_code == 200

    payload = json.loads(response.content.decode("utf-8"))
    assert pref.preference.identifier() == payload["identifier"]
    assert pref.value == payload["value"]


def test_can_update_preference(fake_user, user_client):
    manager = registry.manager(instance=fake_user)
    pref = manager.get_db_pref(section="user", name="favorite_vegetable")
    url = reverse("api:user-detail", kwargs={"pk": pref.preference.identifier()})
    response = user_client.patch(
        url, json.dumps({"value": "P"}), content_type="application/json"
    )
    assert response.status_code == 200

    pref = manager.get_db_pref(section="user", name="favorite_vegetable")

    assert pref.value == "P"


def test_can_update_multiple_preferences(fake_user, user_client):
    manager = registry.manager(instance=fake_user)
    pref = manager.get_db_pref(section="user", name="favorite_vegetable")
    url = reverse("api:user-bulk")
    payload = {
        "user__favorite_vegetable": "C",
        "misc__favourite_colour": "Blue",
    }
    response = user_client.post(
        url, json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 200

    pref1 = manager.get_db_pref(section="user", name="favorite_vegetable")
    pref2 = manager.get_db_pref(section="misc", name="favourite_colour")

    assert pref1.value == "C"
    assert pref2.value == "Blue"


def test_update_preference_returns_validation_error(fake_user, user_client):
    manager = registry.manager(instance=fake_user)
    pref = manager.get_db_pref(section="user", name="favorite_vegetable")
    url = reverse("api:user-detail", kwargs={"pk": pref.preference.identifier()})
    response = user_client.patch(
        url, json.dumps({"value": "Z"}), content_type="application/json"
    )
    assert response.status_code == 400

    payload = json.loads(response.content.decode("utf-8"))

    assert "valid choice" in payload["value"][0]


def test_update_multiple_preferences_with_validation_errors_rollback(
    user_client, fake_user
):
    manager = registry.manager(instance=fake_user)
    pref = manager.get_db_pref(section="user", name="favorite_vegetable")
    url = reverse("api:user-bulk")
    payload = {
        "user__favorite_vegetable": "Z",
        "misc__favourite_colour": "Blue",
    }
    response = user_client.post(
        url, json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 400

    errors = json.loads(response.content.decode("utf-8"))
    assert "valid choice" in errors[pref.preference.identifier()]["value"][0]

    pref1 = manager.get_db_pref(section="user", name="favorite_vegetable")
    pref2 = manager.get_db_pref(section="misc", name="favourite_colour")

    assert pref1.value == pref1.preference.default
    assert pref2.value == pref2.preference.default
