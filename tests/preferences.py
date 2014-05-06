from dynamic_preferences import UserPreference, SitePreference


class BaseTestPref:
    app = "test"

class TestUserPref1(BaseTestPref, UserPreference):
    name = "TestUserPref1"
    default="default value"

class TestUserPref2(BaseTestPref, UserPreference):
    name = "TestUserPref2"


class TestSitePref1(BaseTestPref, SitePreference):
    name = "TestSitePref1"
    default = "site default value"


class TestSitePref2(BaseTestPref, SitePreference):
    name = "TestSitePref2"