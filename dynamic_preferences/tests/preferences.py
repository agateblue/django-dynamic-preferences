from dynamic_preferences import UserPreference, SitePreference
from dynamic_preferences.types import *


class BaseTestPref:
    app = "test"


# User preferences
class TestUserPref1(StringPreference, BaseTestPref, UserPreference):
    name = "TestUserPref1"
    default = "default value"


class TestUserPref2(StringPreference, BaseTestPref, UserPreference):
    name = "TestUserPref2"


class UserBooleanPref(BooleanPreference, BaseTestPref, UserPreference):
    name = "SiteBooleanPref"
    default = False


class UserStringPref(StringPreference, BaseTestPref, UserPreference):
    name = "SUserStringPref"
    default = "Hello world!"

UserBooleanPref().register()
UserStringPref().register()


# Site Preferences
class TestSitePref1(StringPreference, BaseTestPref, SitePreference):
    name = "TestSitePref1"
    default = "site default value"


class TestSitePref2(StringPreference, BaseTestPref, SitePreference):
    name = "TestSitePref2"


class SiteBooleanPref(BooleanPreference, BaseTestPref, SitePreference):
    name = "SiteBooleanPref"
    default = False


class SiteIntPref(IntPreference, BaseTestPref, SitePreference):
    name = "SiteIntPref"
    default = 2


# For testing field instantiation
class TestBooleanPreference(BooleanPreference):
    pass


class TestOverrideBooleanPreference(BooleanPreference):
    field_attributes = {
        "required": False,
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


SiteBooleanPref().register()
SiteIntPref().register()

