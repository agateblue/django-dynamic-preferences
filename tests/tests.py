from django.test import LiveServerTestCase
from dynamic_preferences import UserPreference, SitePreference
from dynamic_preferences import site_preferences, user_preferences
from preferences import TestUserPref1, TestUserPref2, TestSitePref1, TestSitePref2


class TestDynamicPreferences(LiveServerTestCase):

    def setUp(self):
        self.register_default_preferences()

    def register_default_preferences(self):
        self.register_site_preferences()
        self.register_user_preferences()

    def register_user_preferences(self):

        user_preferences.clear()

        self.assertEqual(len(user_preferences), 0)

        user_pref1 = TestUserPref1()
        user_pref1.register()

        self.assertEqual(user_pref1, user_preferences.get(user_pref1.name))
        self.assertEqual(len(user_preferences), 1)

        user_pref2 = TestUserPref2()
        user_pref2.register()

        self.assertEqual(user_pref2, user_preferences.get(user_pref2.name))
        self.assertEqual(len(user_preferences), 2)

    def register_site_preferences(self):

        site_preferences.clear()

        self.assertEqual(len(site_preferences), 0)

        site_pref1 = TestSitePref1()
        site_pref1.register()

        self.assertEqual(site_pref1, site_preferences.get(site_pref1.name))
        self.assertEqual(len(site_preferences), 1)

        site_pref2 = TestSitePref2()
        site_pref2.register()

        self.assertEqual(site_pref2, site_preferences.get(site_pref2.name))
        self.assertEqual(len(site_preferences), 2)

    def test_can_get_preference_value_by_key(self):

        site_pref1 = site_preferences.get("TestSitePref1")
        self.assertEqual(site_pref1.value, TestSitePref1.default)

        user_pref1 = user_preferences.get("TestUserPref1")
        self.assertEqual(user_pref1.value, TestUserPref1.default)

    def test_can_change_preference_value(self):

        site_pref1 = site_preferences.get("TestSitePref1")
        site_pref1.value = "new value"

        self.assertEqual(site_preferences.get("TestSitePref1").value, "new value")

        user_pref1 = user_preferences.get("TestUserPref1")
        user_pref1.value = "new value"

        self.assertEqual(user_preferences.get("TestUserPref1").value, "new value")

