from __future__ import unicode_literals
from django.test import LiveServerTestCase, TestCase
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.template import defaultfilters

from dynamic_preferences.serializers import *
from dynamic_preferences import user_preferences, global_preferences
from dynamic_preferences.models import UserPreferenceModel, GlobalPreferenceModel
from dynamic_preferences.registries import autodiscover, clear
from dynamic_preferences.forms import global_preference_form_builder, user_preference_form_builder

from .types import *
from .test_app.dynamic_preferences_registry import *


class TestTutorial(LiveServerTestCase):
    """
    Test everything from the tutorial
    """
    def setUp(self):
        self.henri = User(username="henri", password="test", email="henri@henri.com")
        self.henri.save()

    def test_quickstart(self):

        registration_allowed_preference, created = GlobalPreferenceModel.objects.get_or_create(section="user",
                                                                            name="registration_allowed")
        registration_is_allowed = registration_allowed_preference.value

        self.assertEqual(registration_is_allowed, False)

        registration_allowed_preference.value = True
        registration_allowed_preference.save()

        self.assertEqual(GlobalPreferenceModel.objects.get(section="user", name="registration_allowed").value, True)

        favorite_colour_preference, created = UserPreferenceModel.objects.get_or_create(section="misc", name="favourite_colour",
                                                                instance=self.henri)
        self.assertEqual(favorite_colour_preference.value, 'Green')

        favorite_colour_preference.value = 'Blue'
        favorite_colour_preference.save()

        self.assertEqual(UserPreferenceModel.objects.get(section="misc", name="favourite_colour", instance=self.henri).value, 'Blue')

        self.assertEqual(self.henri.preferences.get(section="misc", name="favourite_colour").value, 'Blue')

class TestModels(LiveServerTestCase):
    def test_can_save_and_retrieve_preference_with_section_none(self):
        no_section_pref = global_preferences.get(name="no_section")
        instance = no_section_pref.to_model()
        instance.save()

        self.assertEqual(GlobalPreferenceModel.objects.filter(section=None, name="no_section").count(), 1)

    def test_adding_user_create_default_preferences(self):

        u = User(username="post_create")
        u.save()

        self.assertEqual(u.preferences.count(), len(user_preferences.preferences()))

class TestDynamicPreferences(LiveServerTestCase):

    def setUp(self):

        self.test_user = User(username="test", password="test", email="test@test.com")
        self.test_user.save()

    def test_can_get_preference_value_by_key(self):

        user_pref1 = user_preferences.get("TestUserPref1", "test")
        print(user_preferences)
        self.assertEqual(user_pref1.default, TestUserPref1.default)

    def test_can_change_user_preference_value(self):

        user_pref1 = user_preferences.get("TestUserPref1", "test")
        user_pref1.value = "new value"

        self.assertEqual(user_preferences.get("TestUserPref1","test").value, "new value")

    def test_preference_is_saved_to_database(self):

        user_pref1 = user_preferences.get("TestUserPref1", "test")
        p = user_pref1.to_model(instance=self.test_user)
        p.value = 'new test value'
        p.save()
        test_user_pref1 = UserPreferenceModel.objects.get(section="test", name="TestUserPref1", instance=self.test_user)

        self.assertEqual(user_pref1, test_user_pref1.preference)
        self.assertEqual(test_user_pref1.section, "test")
        self.assertEqual(test_user_pref1.name, "TestUserPref1")
        self.assertEqual(test_user_pref1.value, "new test value")

    def test_user_preference_is_saved_to_database(self):
        user = User(username="hello")
        user.save()

        user_pref1 = user_preferences.get("TestUserPref1", "test")
        instance = user_pref1.to_model(instance=user)
        instance.value = "new user value"
        instance.save()

        test_user_pref1 = UserPreferenceModel.objects.get(section="test", name="TestUserPref1", instance=user)
        self.assertEqual(user_pref1, test_user_pref1.preference)
        self.assertEqual(test_user_pref1.section, "test")
        self.assertEqual(test_user_pref1.name, "TestUserPref1")
        self.assertEqual(test_user_pref1.value, "new user value")

    def test_per_instance_preference_stay_unique_in_db(self):

        user_pref1 = user_preferences.get("TestUserPref1", "test")
        user_pref1.to_model(instance=self.test_user, value="new value")

        duplicate = UserPreferenceModel(section="test", name="TestUserPref1", instance=self.test_user)

        with self.assertRaises(IntegrityError):
            duplicate.save()

    def test_preference_value_set_to_default(self):

        pref = user_preferences.get("TestUserPref1", "test")
        pref.to_model(instance=self.test_user)

        instance = UserPreferenceModel.objects.get(section="test", name="TestUserPref1", instance=self.test_user)
        self.assertEqual(pref.default, instance.value)

    def test_preference_model_manager_to_dict(self):
        call_command('checkpreferences', verbosity=1, interactive=False)
        expected = {u'test': {u'TestGlobal1': u'default value', u'TestGlobal2': False, u'TestGlobal3': False}, None: {u'no_section': False}, u'user': {u'max_users': 100, u'items_per_page': 25, u'registration_allowed': False}}
        self.assertDictEqual(GlobalPreferenceModel.objects.to_dict(), expected)

    def test_user_preference_model_manager_to_dict(self):
        user = self.test_user
        expected = {u'misc': {u'favourite_colour': u'Green', u'is_zombie': True}, u'user': {u'favorite_vegetable': 'C'}, u'test': {u'SUserStringPref': u'Hello world!', u'SiteBooleanPref': False, u'TestUserPref1': u'default value', u'TestUserPref2': u''}}
        self.assertEqual(UserPreferenceModel.objects.to_dict(instance=user), expected)

class TestPreferenceObjects(LiveServerTestCase):

    def test_can_get_to_string_notation(self):
        pref = global_preferences.get('user.registration_allowed')

        self.assertEqual(pref.identifier(), 'user.registration_allowed')
        self.assertEqual(pref.identifier("__"), 'user__registration_allowed')

    def test_boolean_field_class_instantiation(self):

        preference = TestBooleanPreference()

        self.assertEqual(preference.field.initial, False)

    def test_char_field_class_instantiation(self):

        preference = TestStringPreference()

        self.assertEqual(preference.field.initial, "hello world!")

    def test_choice_field(self):
        #preference = TestChoicePreference()
        pass
        #self.assertEqual(preference.field.initial, "FR")

class TestRegistry(LiveServerTestCase):

    def test_can_retrieve_preference_using_dotted_notation(self):
        registration_allowed = global_preferences.get(name="registration_allowed", section="user")
        dotted_result = global_preferences.get("user.registration_allowed")
        self.assertEqual(registration_allowed, dotted_result)

    def test_can_register_and_retrieve_preference_with_section_none(self):
        no_section_pref = global_preferences.get(name="no_section")
        self.assertEqual(no_section_pref.section, None)

    def test_can_autodiscover_multiple_times(self):
        autodiscover()
        self.assertEqual(len(global_preferences.preferences()), 7)
        self.assertEqual(len(user_preferences.preferences()), 7)
        autodiscover()
        self.assertEqual(len(global_preferences.preferences()), 7)
        self.assertEqual(len(user_preferences.preferences()), 7)

    def test_can_autodiscover_user_preferences(self):

        clear()
        with self.assertRaises(KeyError):
            user_preferences.preferences(section='test')

        autodiscover(force_reload=True)

        self.assertEqual(len(user_preferences.preferences(section='test')), 4)


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

   
class TestViews(LiveServerTestCase):

    def setUp(self):
        self.henri = User(username="henri", password="test", email="henri@henri.com")
        self.henri.set_password('test')
        self.henri.save()

        self.admin = User(username="admin", email="admin@admin.com", is_superuser=True, is_staff=True)
        self.admin.set_password('test')
        self.admin.save()
    def test_can_build_global_preference_form(self):
        # We want to display a form with two global preferences
        # RegistrationAllowed and MaxUsers
        form = global_preference_form_builder(preferences=['user.registration_allowed', "user.max_users"])()

        self.assertEqual(len(form.fields), 2)
        self.assertEqual(form.fields['user.registration_allowed'].initial, False)

    def test_can_build_preference_form_from_sections(self):
        form = global_preference_form_builder(section='test')()

        self.assertEqual(len(form.fields), 3)

    def test_can_build_global_preference_form_from_sections(self):
        form = global_preference_form_builder(section='test')()

        self.assertEqual(len(form.fields), 3)

    def test_can_build_user_preference_form_from_sections(self):
        form = user_preference_form_builder(instance=self.admin, section='test')()

        self.assertEqual(len(form.fields), 4)

    def test_global_preference_view_requires_staff_member(self):
        url = reverse("dynamic_preferences.global")
        response = self.client.get(url, follow=True)

        self.assertRedirects(response, "/admin/login/?next=/global/")

        self.client.login(username='henri', password="test")
        response = self.client.get(url)
        self.assertRedirects(response, "/admin/login/?next=/global/")

        self.client.login(username='admin', password="test")
        response = self.client.get(url)

        self.assertEqual(self.admin.is_authenticated(), True)
        self.assertEqual(response.status_code, 200)

    def test_global_preference_view_display_form(self):

        url = reverse("dynamic_preferences.global")
        self.client.login(username='admin', password="test")
        response = self.client.get(url)
        self.assertEqual(len(response.context['form'].fields), 7)
        self.assertEqual(response.context['registry'], global_preferences)

    def test_global_preference_filters_by_section(self):
        self.client.login(username='admin', password="test")
        url = reverse("dynamic_preferences.global.section", kwargs={"section": 'user'})
        response = self.client.get(url)
        self.assertEqual(len(response.context['form'].fields), 3)

    def test_preference_are_updated_on_form_submission(self):
        self.client.login(username='admin', password="test")
        url = reverse("dynamic_preferences.global.section", kwargs={"section": 'user'})
        response = self.client.post(url, {'user.max_users': 95, 'user.registration_allowed': True,
                                          "user.items_per_page": 12})
        self.assertEqual(GlobalPreferenceModel.objects.get(section="user", name="max_users").value, 95)
        self.assertEqual(GlobalPreferenceModel.objects.get(section="user", name="registration_allowed").value, True)
        self.assertEqual(GlobalPreferenceModel.objects.get(section="user", name="items_per_page").value, 12)

    def test_user_preference_form_is_bound_with_current_user(self):
        self.client.login(username='henri', password="test")
        self.assertEqual(UserPreferenceModel.objects.get_or_create(instance=self.henri, section="misc", name='favourite_colour')[0].value, 'Green')
        self.assertEqual(UserPreferenceModel.objects.get_or_create(instance=self.henri, section="misc", name='is_zombie')[0].value, True)

        url = reverse("dynamic_preferences.user.section", kwargs={'section': 'misc'})
        response = self.client.post(url, {'misc.favourite_colour': 'Purple', 'misc.is_zombie': False})

        self.assertEqual(self.henri.preferences.get(section="misc", name='favourite_colour').value, 'Purple')
        self.assertEqual(self.henri.preferences.get(section="misc", name='is_zombie').value, False)

    def test_template_gets_global_preferences_via_template_processor(self):
        url = reverse("dynamic_preferences.test.templateview")
        response = self.client.get(url)
        self.assertEqual(response.context['global_preferences'], GlobalPreferenceModel.objects.to_dict())

    def test_template_gets_user_preferences_via_template_processor(self):
        user = User.objects.get(pk=self.henri.pk)
        self.client.login(username=user.username, password="test")
        url = reverse("dynamic_preferences.test.templateview")
        response = self.client.get(url)
        to_dict = UserPreferenceModel.objects.to_dict(instance=user)
        self.assertEqual(response.context['user_preferences'], to_dict)