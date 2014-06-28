from dynamic_preferences.preferences import UserPreference, SitePreference, GlobalPreference
from dynamic_preferences.types import *
from dynamic_preferences.registries import register


# Tutorial preferences

@register
class RegistrationAllowed(BooleanPreference, GlobalPreference):
    """
    Are new registrations allowed ?
    """
    section = "user"
    name = "registration_allowed"
    default = False


@register
class FavoriteColour(StringPreference, UserPreference):
    """
    What's your favorite colour ?
    """
    section = "misc"
    name = "favorite_colour"
    default = "Green"


class BaseTestPref:
    section = "test"


# User preferences
@register
class TestUserPref1(StringPreference, BaseTestPref, UserPreference):
    name = "TestUserPref1"
    default = "default value"

@register
class TestUserPref2(StringPreference, BaseTestPref, UserPreference):
    name = "TestUserPref2"

@register
class UserBooleanPref(BooleanPreference, BaseTestPref, UserPreference):
    name = "SiteBooleanPref"
    default = False

@register
class UserStringPref(StringPreference, BaseTestPref, UserPreference):
    name = "SUserStringPref"
    default = "Hello world!"


# Site Preferences
@register
class TestSitePref1(StringPreference, BaseTestPref, SitePreference):
    name = "TestSitePref1"
    default = "site default value"

@register
class TestSitePref2(StringPreference, BaseTestPref, SitePreference):
    name = "TestSitePref2"

@register
class SiteBooleanPref(BooleanPreference, BaseTestPref, SitePreference):
    name = "SiteBooleanPref"
    default = False

@register
class SiteIntPref(IntPreference, BaseTestPref, SitePreference):
    name = "SiteIntPref"
    default = 2

# Global
@register
class TestGlobal1(StringPreference, BaseTestPref, GlobalPreference):
    name = "TestGlobal1"
    default = "default value"


@register
class TestGlobal2(BooleanPreference, BaseTestPref, GlobalPreference):
    name = "TestGlobal2"
    default = False


@register
class TestGlobal3(BooleanPreference, BaseTestPref, GlobalPreference):
    name = "TestGlobal3"
    default = False


# For testing field instantiation
class TestBooleanPreference(BooleanPreference):
    pass

class TestOverrideBooleanPreference(BooleanPreference):
    field_attributes = {
        "required": True,
        "initial": True
    }

class TestStringPreference(StringPreference):

    field_attributes = {
        "initial": "hello world!"
    }

class TestChoicePreference(ChoicePreference):

    choices = (
        ("FR", "French"),
        ("EN", "English"),
        ("DE", "Deutsch")
    )

    field_attributes = {
        "initial": "FR",
        "choices": choices
    }


