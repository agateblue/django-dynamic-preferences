from dynamic_preferences import UserPreference, SitePreference, GlobalPreference
from dynamic_preferences.types import *


class BaseTestPref:
    app = "test"


#global prefs
class TestGlobal11(StringPreference, BaseTestPref, GlobalPreference):
    name = "TestGlobal1"
    default = "default value"

TestGlobal11().register()

