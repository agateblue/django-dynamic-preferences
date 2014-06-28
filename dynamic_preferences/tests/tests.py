from django.test import LiveServerTestCase
from dynamic_preferences.preferences import site_preferences, user_preferences, global_preferences, SitePreference, UserPreference
from dynamic_preferences.models import SitePreferenceModel, UserPreferenceModel
from dynamic_preferences_registry import *
from dynamic_preferences.models import PreferenceSite, PreferenceUser, UserPreferenceModel, SitePreferenceModel
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import IntegrityError
from dynamic_preferences.serializers import *
from django.template import defaultfilters


site_preferences.test, user_preferences.test, global_preferences.test = True, True, True


class TestDynamicPreferences(LiveServerTestCase):

    def setUp(self):
        self.register_default_preferences()

        self.test_user = PreferenceUser(username="test", password="test", email="test@test.com")
        self.test_user.save()

        self.test_site = PreferenceSite(domain="www.test.com", name="test")
        self.test_site.save()

    def register_default_preferences(self):
        self.register_site_preferences()
        self.register_user_preferences()

    def register_user_preferences(self):

        user_preferences.clear()

        self.assertEqual(len(user_preferences), 0)

        user_pref1 = TestUserPref1()
        user_pref1.register()

        self.assertEqual(user_pref1, user_preferences.get("test", user_pref1.name))
        self.assertEqual(len(user_preferences['test']), 1)

        user_pref2 = TestUserPref2()
        user_pref2.register()

        self.assertEqual(user_pref2, user_preferences.get("test", user_pref2.name))
        self.assertEqual(len(user_preferences['test']), 2)

    def register_site_preferences(self):

        site_preferences.clear()

        self.assertEqual(len(site_preferences), 0)

        site_pref1 = TestSitePref1()
        site_pref1.register()

        self.assertEqual(site_pref1, site_preferences.get("test", site_pref1.name))
        self.assertEqual(len(site_preferences['test']), 1)

        site_pref2 = TestSitePref2()
        site_pref2.register()
        self.assertEqual(site_pref2, site_preferences.get("test", site_pref2.name))
        self.assertEqual(len(site_preferences['test']), 2)

    def test_can_get_preference_value_by_key(self):

        site_pref1 = site_preferences.get("test", "TestSitePref1")
        self.assertEqual(site_pref1.default, TestSitePref1.default)

        user_pref1 = user_preferences.get("test", "TestUserPref1")
        self.assertEqual(user_pref1.default, TestUserPref1.default)

    def test_can_change_site_preference_value(self):

        site_pref1 = site_preferences.get("test", "TestSitePref1")
        site_pref1.value = "new value"

        self.assertEqual(site_preferences.get("test", "TestSitePref1").value, "new value")

        user_pref1 = user_preferences.get("test", "TestUserPref1")
        user_pref1.value = "new value"

        self.assertEqual(user_preferences.get("test", "TestUserPref1").value, "new value")

    def test_site_preference_is_saved_to_database(self):

        site_pref1 = site_preferences.get("test", "TestSitePref1")
        site_pref1.to_model(site=self.test_site, value="new site value")

        test_site_pref1 = SitePreferenceModel.objects.get(app="test", name="TestSitePref1", site=self.test_site)
        self.assertEqual(site_pref1, test_site_pref1.preference)
        self.assertEqual(test_site_pref1.app, "test")
        self.assertEqual(test_site_pref1.name, "TestSitePref1")
        self.assertEqual(test_site_pref1.value, "new site value")

    def test_user_preference_is_saved_to_database(self):

        user_pref1 = user_preferences.get("test", "TestUserPref1")
        instance = user_pref1.to_model(user=self.test_user, value="new user value")

        test_user_pref1 = UserPreferenceModel.objects.get(app="test", name="TestUserPref1", user=self.test_user)
        self.assertEqual(user_pref1, test_user_pref1.preference)
        self.assertEqual(test_user_pref1.app, "test")
        self.assertEqual(test_user_pref1.name, "TestUserPref1")
        self.assertEqual(test_user_pref1.value, "new user value")

    def test_site_preference_stay_unique_in_db(self):

        site_pref1 = site_preferences.get("test", "TestSitePref1")
        site_pref1.to_model(site=self.test_site, value="new value")

        duplicate = SitePreferenceModel(app="test", name="TestSitePref1", site=self.test_site)

        with self.assertRaises(IntegrityError):
            duplicate.save()

    def test_user_preference_stay_unique_in_db(self):

        user_pref1 = user_preferences.get("test", "TestUserPref1")
        user_pref1.to_model(user=self.test_user, value="new value")

        duplicate = UserPreferenceModel(app="test", name="TestUserPref1", user=self.test_user)

        with self.assertRaises(IntegrityError):
            duplicate.save()

    def test_preference_value_set_to_default(self):

        pref = user_preferences.get("test", "TestUserPref1")
        pref.to_model(user=self.test_user)

        instance = UserPreferenceModel.objects.get(app="test", name="TestUserPref1", user=self.test_user)
        self.assertEqual(pref.default, instance.value)

        pref = site_preferences.get("test", "TestSitePref1")
        pref.to_model(site=self.test_site)

        instance = SitePreferenceModel.objects.get(app="test", name="TestSitePref1", site=self.test_site)
        self.assertEqual(pref.default, instance.value)


class TestPreferenceObjects(LiveServerTestCase):

    def test_boolean_field_class_instantiation(self):

        preference = TestBooleanPreference()

        self.assertEqual(preference.field.initial, None)
        self.assertEqual(preference.field.required, False)

        preference = TestOverrideBooleanPreference()

        self.assertEqual(preference.field.initial, True)
        self.assertEqual(preference.field.required, True)

    def test_char_field_class_instantiation(self):

        preference = TestStringPreference()

        self.assertEqual(preference.field.initial, "hello world!")

    def test_choices_field_instantiation(self):
        preference = TestChoicePreference()

        self.assertEqual(len(preference.field.choices), 3)
        self.assertEqual(preference.field.initial, "FR")


class TestRegistry(LiveServerTestCase):

    def test_can_autodiscover_site_preferences(self):
        site_preferences.clear()
        with self.assertRaises(KeyError):
            site_preferences.preferences(app='test')
        site_preferences.autodiscover(force_reload=True)

        self.assertEqual(len(site_preferences.preferences(app='test')), 2)

    def test_can_autodiscover_user_preferences(self):

        user_preferences.clear()
        with self.assertRaises(KeyError):
            user_preferences.preferences(app='test')

        user_preferences.autodiscover(force_reload=True)

        self.assertEqual(len(user_preferences.preferences(app='test')), 2)


class TestSerializers(LiveServerTestCase):

    def test_boolean_serialization(self):
        s = BooleanSerializer

        self.assertEqual(s.serialize(True), "1")
        self.assertEqual(s.serialize("True"), "1")
        self.assertEqual(s.serialize("Something"), "1")


        self.assertEqual(s.serialize(False), "0")
        self.assertEqual(s.serialize(""), "0")

    def test_boolean_deserialization(self):

        s = BooleanSerializer

        for v in s.true:
            self.assertEqual(s.deserialize(v), True)

        for v in s.false:
            self.assertEqual(s.deserialize(v), False)

        with self.assertRaises(s.exception):
            s.deserialize("I'm a true value")

    def test_int_serialization(self):

        s = IntSerializer

        self.assertEqual(s.serialize(1), "1")
        self.assertEqual(s.serialize(666), "666")
        self.assertEqual(s.serialize(-144), "-144")
        self.assertEqual(s.serialize(0), "0")
        self.assertEqual(s.serialize(123456), "123456")

        with self.assertRaises(s.exception):
            s.serialize("I'm an integer")

    def test_int_deserialization(self):

        s = IntSerializer

        self.assertEqual(s.deserialize("1"), 1)
        self.assertEqual(s.deserialize("125"), 125)
        self.assertEqual(s.deserialize("-144000"), -144000)
        self.assertEqual(s.deserialize("0"), 0)

        with self.assertRaises(s.exception):
            s.deserialize("Trust me, i'm an integer")

    def test_string_serialization(self):

        s = StringSerializer

        self.assertEqual(s.serialize("Bonjour"), "Bonjour")
        self.assertEqual(s.serialize("12"), "12")
        self.assertEqual(s.serialize("I'm a long sentence, but I rock"), "I'm a long sentence, but I rock")

        # check for HTML escaping
        kwargs = {"escape_html": True,}
        self.assertEqual(
            s.serialize("<span>Please, I don't wanna disappear</span>", **kwargs),
            defaultfilters.force_escape("<span>Please, I don't wanna disappear</span>")
        )

        with self.assertRaises(s.exception):
            s.serialize(('I', 'Want', 'To', 'Be', 'A', 'String'))

    def test_string_deserialization(self):

        s = StringSerializer
        self.assertEqual(s.deserialize("Bonjour"), "Bonjour")
        self.assertEqual(s.deserialize("12"), "12")
        self.assertEqual(s.deserialize("I'm a long sentence, but I rock"), "I'm a long sentence, but I rock")

        kwargs = {"escape_html": True,}
        self.assertEqual(
            s.deserialize(s.serialize("<span>Please, I don't wanna disappear</span>", **kwargs)),
            defaultfilters.force_escape("<span>Please, I don't wanna disappear</span>")
        )

        with self.assertRaises(s.exception):
            s.deserialize({"FOR": "THE", "H":0, "R":"DE!!"})