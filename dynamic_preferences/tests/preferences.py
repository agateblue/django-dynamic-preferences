from dynamic_preferences import UserPreference, SitePreference
from dynamic_preferences.types import *

class BaseTestPref:
    app = "test"


class TestUserPref1(StringPreference, BaseTestPref, UserPreference):
    name = "TestUserPref1"
    default = "default value"


class TestUserPref2(StringPreference, BaseTestPref, UserPreference):
    name = "TestUserPref2"


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

SiteBooleanPref().register()
SiteIntPref().register()

