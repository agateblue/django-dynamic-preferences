from __future__ import unicode_literals
import pytest

from django.contrib.auth.models import User

from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.users.models import UserPreferenceModel


def test_quickstart(henri):
    global_preferences = global_preferences_registry.manager()

    assert global_preferences["user__registration_allowed"] is False

    global_preferences["user__registration_allowed"] = True

    assert global_preferences["user__registration_allowed"] is True
    assert (
        GlobalPreferenceModel.objects.get(
            section="user", name="registration_allowed"
        ).value
        is True
    )

    assert henri.preferences["misc__favourite_colour"] == "Green"

    henri.preferences["misc__favourite_colour"] = "Blue"

    assert henri.preferences["misc__favourite_colour"] == "Blue"

    assert (
        UserPreferenceModel.objects.get(
            section="misc", name="favourite_colour", instance=henri
        ).value
        == "Blue"
    )
