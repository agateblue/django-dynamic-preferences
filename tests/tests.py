from __future__ import unicode_literals
from django.test import LiveServerTestCase, TestCase
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.core.cache import caches
from django.db import IntegrityError
from django.template import defaultfilters
from decimal import Decimal

from dynamic_preferences.serializers import *
from dynamic_preferences import user_preferences_registry, global_preferences_registry
from dynamic_preferences.models import UserPreferenceModel, GlobalPreferenceModel
from dynamic_preferences.registries import autodiscover, clear
from dynamic_preferences.managers import PreferencesManager
from dynamic_preferences import exceptions
from dynamic_preferences.forms import global_preference_form_builder, user_preference_form_builder
from dynamic_preferences.preferences import EMPTY_SECTION
from .types import *
from .test_app.dynamic_preferences_registry import *


class BaseTest(object):

    def tearDown(self):
        caches['default'].clear()


class TestTutorial(BaseTest, TestCase):

    """
    Test everything from the tutorial
    """

    def setUp(self):
        self.henri = User(
            username="henri", password="test", email="henri@henri.com")
        self.henri.save()

    def test_quickstart(self):
        global_preferences = global_preferences_registry.manager()

        self.assertEqual(global_preferences['user__registration_allowed'], False)

        global_preferences['user__registration_allowed'] = True

        self.assertEqual(global_preferences['user__registration_allowed'], True)
        self.assertEqual(GlobalPreferenceModel.objects.get(
            section="user", name="registration_allowed").value, True)


        self.assertEqual(self.henri.preferences['misc__favourite_colour'], 'Green')

        self.henri.preferences['misc__favourite_colour'] = 'Blue'

        self.assertEqual(self.henri.preferences['misc__favourite_colour'], 'Blue')

        self.assertEqual(UserPreferenceModel.objects.get(
            section="misc", name="favourite_colour", instance=self.henri).value, 'Blue')



class TestModels(BaseTest, TestCase):

    def test_adding_user_create_default_preferences(self):

        u = User(username="post_create")
        u.save()

        self.assertEqual(
            len(u.preferences), len(user_preferences_registry.preferences()))

    def test_global_preferences_manager_get(self):
        global_preferences = global_preferences_registry.manager()
        self.assertEqual(global_preferences['no_section'], False)

    def test_global_preferences_manager_set(self):
        global_preferences = global_preferences_registry.manager()
        global_preferences['no_section'] = True
        self.assertEqual(global_preferences['no_section'], True)

    def test_can_cache_single_preference(self):

        manager = global_preferences_registry.manager()
        v = manager['no_section']
        with self.assertNumQueries(0):
            v = manager['no_section']
            v = manager['no_section']
            v = manager['no_section']

    def test_can_cache_all_preferences(self):

        manager = global_preferences_registry.manager()
        manager.all()
        with self.assertNumQueries(0):
            manager.all()
            manager.all()
            manager.all()

    def test_global_preferences_manager_by_name(self):
        manager = global_preferences_registry.manager()
        self.assertEqual(manager.by_name()['max_users'], manager['user__max_users'])
        self.assertEqual(len(manager.all()), len(manager.by_name()))

    def test_global_preferences_manager_get_by_name(self):
        manager = global_preferences_registry.manager()
        self.assertEqual(manager.get_by_name('max_users'), manager['user__max_users'])
        
    def test_cache_invalidate_on_save(self):

        manager = global_preferences_registry.manager()
        model_instance = manager.create_db_pref(section=None, name='no_section', value=False)

        with self.assertNumQueries(0):
            assert not manager['no_section']
            manager['no_section']

        model_instance.value = True
        model_instance.save()

        with self.assertNumQueries(0):
            assert manager['no_section']
            manager['no_section']


class TestDynamicPreferences(BaseTest, TestCase):

    def setUp(self):

        self.test_user = User(
            username="test", password="test", email="test@test.com")
        self.test_user.save()

    def test_manager_is_attached_to_each_referenced_instance(self):
        self.assertTrue(isinstance(self.test_user.preferences, PreferencesManager))

    def test_preference_is_saved_to_database(self):

        self.test_user.preferences['test__TestUserPref1'] = 'new test value'

        test_user_pref1 = UserPreferenceModel.objects.get(
            section="test", name="TestUserPref1", instance=self.test_user)

        self.assertEqual(self.test_user.preferences['test__TestUserPref1'], "new test value")

    def test_per_instance_preference_stay_unique_in_db(self):

        self.test_user.preferences['test__TestUserPref1'] = 'new value'

        duplicate = UserPreferenceModel(
            section="test", name="TestUserPref1", instance=self.test_user)

        with self.assertRaises(IntegrityError):
            duplicate.save()

    def test_preference_value_set_to_default(self):

        pref = user_preferences_registry.get("TestUserPref1", "test")

        value = self.test_user.preferences['test__TestUserPref1']
        self.assertEqual(pref.default, value)
        instance = UserPreferenceModel.objects.get(
            section="test", name="TestUserPref1", instance=self.test_user)

    def test_preference_model_manager_to_dict(self):
        manager = global_preferences_registry.manager()
        call_command('checkpreferences', verbosity=1, interactive=False)
        expected = {
            u'test__TestGlobal1': u'default value',
            u'test__TestGlobal2': False,
            u'test__TestGlobal3': False,
            u'no_section': False,
            u'user__max_users': 100,
            u'user__items_per_page': 25,
            u'blog__featured_entry': None,
            u'user__registration_allowed': False}
        self.assertDictEqual(manager.all(), expected)

    def test_user_preference_model_manager_to_dict(self):
        user = self.test_user
        expected = {
            u'misc__favourite_colour': u'Green',
            u'misc__is_zombie': True,
            u'user__favorite_vegetable': 'C',
            u'test__SUserStringPref': u'Hello world!',
            u'test__SiteBooleanPref': False,
            u'test__TestUserPref1': u'default value',
            u'test__TestUserPref2': u'default value',
        }
        self.assertEqual(
            user.preferences.all(), expected)


class TestPreferenceObjects(BaseTest, TestCase):

    def test_can_get_to_string_notation(self):
        pref = global_preferences_registry.get('user__registration_allowed')

        self.assertEqual(pref.identifier(), 'user__registration_allowed')

    def test_preference_requires_default_value(self):
        with self.assertRaises(exceptions.MissingDefault):
            preference = NoDefault()

    def test_default_accepts_callable(self):

        class P(IntPreference):
            def get_default(self):
                return 4

        self.assertEqual(P().get('default'), 4)

    def test_getter(self):
        class PNoGetter(IntPreference):
            default = 1
            help_text = 'Hello'

        class PGetter(IntPreference):
            def get_default(self):
                return 1

            def get_help_text(self):
                return 'Hello'

        p_no_getter = PNoGetter()
        p_getter = PGetter()
        for attribute, expected in [('default', 1), ('help_text', 'Hello')]:
            self.assertEqual(p_no_getter.get(attribute), expected)
            self.assertEqual(p_getter.get(attribute), expected)

    def test_field(self):
        class P(IntPreference):
            default = 1
            verbose_name = 'P'
        p = P()

        self.assertEqual(p.field.initial, 1)
        self.assertEqual(p.field.label, 'P')
        self.assertEqual(p.field.__class__, forms.IntegerField)

    def test_boolean_field_class_instantiation(self):

        class P(BooleanPreference):
            default = False
        preference = P()
        self.assertEqual(preference.field.initial, False)

    def test_char_field_class_instantiation(self):
        class P(StringPreference):
            default = "hello world!"
        preference = P()

        self.assertEqual(preference.field.initial, "hello world!")

    def test_longstring_preference_widget(self):
        class P(LongStringPreference):
            default = "hello world!"
        preference = P()

        self.assertTrue(isinstance(preference.field.widget, forms.Textarea))

    def test_decimal_preference(self):
        class P(DecimalPreference):
            default = Decimal('2.5')
        preference = P()

        self.assertEqual(preference.field.initial, Decimal('2.5'))

    def test_float_preference(self):
        class P(FloatPreference):
            default = 0.35
        preference = P()

        self.assertEqual(preference.field.initial, 0.35)
        self.assertNotEqual(preference.field.initial, 0.3)
        self.assertNotEqual(preference.field.initial, 0.3001)
    
    def test_multiple_choice_preference(self):
        class P(MultipleChoicePreference):
            choices = (('apple', 'Apple'), ('orange', 'Orange'), ('pear', 'Pear'))
            default = ['apple', 'pear']
        preference = P()

        self.assertEqual(preference.field.initial, ['apple', 'pear'])
        self.assertNotEqual(preference.field.initial, 'apple')

class TestRegistry(BaseTest, TestCase):

    def test_can_retrieve_preference_using_dotted_notation(self):
        registration_allowed = global_preferences_registry.get(
            name="registration_allowed", section="user")
        dotted_result = global_preferences_registry.get(
            "user__registration_allowed")
        self.assertEqual(registration_allowed, dotted_result)

    def test_can_register_and_retrieve_preference_with_section_none(self):
        no_section_pref = global_preferences_registry.get(name="no_section")
        self.assertEqual(no_section_pref.section, EMPTY_SECTION)

    def test_can_autodiscover_multiple_times(self):
        autodiscover()
        self.assertEqual(len(global_preferences_registry.preferences()), 8)
        self.assertEqual(len(user_preferences_registry.preferences()), 7)
        autodiscover()
        self.assertEqual(len(global_preferences_registry.preferences()), 8)
        self.assertEqual(len(user_preferences_registry.preferences()), 7)

    def test_can_autodiscover_user_preferences(self):

        clear()
        with self.assertRaises(KeyError):
            user_preferences_registry.preferences(section='test')

        autodiscover(force_reload=True)

        self.assertEqual(
            len(user_preferences_registry.preferences(section='test')), 4)


class TestSerializers(BaseTest, TestCase):

    def test_boolean_serialization(self):
        s = BooleanSerializer

        self.assertEqual(s.serialize(True), "True")
        self.assertEqual(s.serialize(False), "False")
        with self.assertRaises(s.exception):
            s.serialize('yolo')

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

    def test_decimal_serialization(self):

        s = DecimalSerializer

        self.assertEqual(s.serialize(Decimal("1")), "1")
        self.assertEqual(s.serialize(Decimal("-1")), "-1")
        self.assertEqual(s.serialize(Decimal("-666.6")), "-666.6")
        self.assertEqual(s.serialize(Decimal("666.6")), "666.6")

        with self.assertRaises(s.exception):
            s.serialize("I'm a decimal")

    def test_float_serialization(self):

        s = FloatSerializer

        self.assertEqual(s.serialize(1.0), "1.0")
        self.assertEqual(s.serialize(-1.0), "-1.0")
        self.assertEqual(s.serialize(-666.6), "-666.6")
        self.assertEqual(s.serialize(666.6), "666.6")

        with self.assertRaises(s.exception):
            s.serialize("I'm a float")

    def test_float_deserialization(self):

        s = FloatSerializer

        self.assertEqual(s.deserialize("1.0"), float("1.0"))
        self.assertEqual(s.deserialize("-1.0"), float("-1.0"))
        self.assertEqual(s.deserialize("-666.6"), float("-666.6"))
        self.assertEqual(s.deserialize("666.6"), float("666.6"))

        with self.assertRaises(s.exception):
            s.serialize("I'm a float")

    def test_int_deserialization(self):

        s = DecimalSerializer

        self.assertEqual(s.deserialize("1"), Decimal("1"))
        self.assertEqual(s.deserialize("-1"), Decimal("-1"))
        self.assertEqual(s.deserialize("-666.6"), Decimal("-666.6"))
        self.assertEqual(s.deserialize("666.6"), Decimal("666.6"))

        with self.assertRaises(s.exception):
            s.serialize("I'm a decimal!")

    def test_string_serialization(self):

        s = StringSerializer

        self.assertEqual(s.serialize("Bonjour"), "Bonjour")
        self.assertEqual(s.serialize("12"), "12")
        self.assertEqual(s.serialize(
            "I'm a long sentence, but I rock"), "I'm a long sentence, but I rock")

        # check for HTML escaping
        kwargs = {"escape_html": True, }
        self.assertEqual(
            s.serialize(
                "<span>Please, I don't wanna disappear</span>", **kwargs),
            defaultfilters.force_escape(
                "<span>Please, I don't wanna disappear</span>")
        )

        with self.assertRaises(s.exception):
            s.serialize(('I', 'Want', 'To', 'Be', 'A', 'String'))

    def test_string_deserialization(self):

        s = StringSerializer
        self.assertEqual(s.deserialize("Bonjour"), "Bonjour")
        self.assertEqual(s.deserialize("12"), "12")
        self.assertEqual(s.deserialize(
            "I'm a long sentence, but I rock"), "I'm a long sentence, but I rock")

        kwargs = {"escape_html": True, }
        self.assertEqual(
            s.deserialize(
                s.serialize("<span>Please, I don't wanna disappear</span>", **kwargs)),
            defaultfilters.force_escape(
                "<span>Please, I don't wanna disappear</span>")
        )

    def test_list_serialization(self):
        s = ListSerializer
        self.assertEqual(s.serialize(['apple', 'orange']), 'apple,orange')
        self.assertEqual(s.serialize(['apple,orange', 'pear']), '"apple,orange",pear')
        self.assertEqual(s.serialize(['apple"', 'orange']), '"apple""",orange')
    
    def test_list_deserialization(self):
        s = ListSerializer
        self.assertEqual(s.deserialize('apple,orange'), ['apple', 'orange'])
        self.assertEqual(s.deserialize('"apple,orange",pear'), ['apple,orange', 'pear'])
        self.assertEqual(s.deserialize('"apple""",orange'), ['apple"', 'orange'])


class TestViews(BaseTest, LiveServerTestCase):

    def setUp(self):
        self.henri = User(
            username="henri", password="test", email="henri@henri.com")
        self.henri.set_password('test')
        self.henri.save()

        self.admin = User(
            username="admin", email="admin@admin.com", is_superuser=True, is_staff=True)
        self.admin.set_password('test')
        self.admin.save()

    def test_can_build_global_preference_form(self):
        # We want to display a form with two global preferences
        # RegistrationAllowed and MaxUsers
        form = global_preference_form_builder(
            preferences=['user__registration_allowed', "user__max_users"])()

        self.assertEqual(len(form.fields), 2)
        self.assertEqual(
            form.fields['user__registration_allowed'].initial, False)

    def test_can_build_preference_form_from_sections(self):
        form = global_preference_form_builder(section='test')()

        self.assertEqual(len(form.fields), 3)

    def test_can_build_global_preference_form_from_sections(self):
        form = global_preference_form_builder(section='test')()

        self.assertEqual(len(form.fields), 3)

    def test_can_build_user_preference_form_from_sections(self):
        form = user_preference_form_builder(
            instance=self.admin, section='test')()

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
        self.assertEqual(len(response.context['form'].fields), 8)
        self.assertEqual(
            response.context['registry'], global_preferences_registry)

    def test_global_preference_filters_by_section(self):
        self.client.login(username='admin', password="test")
        url = reverse(
            "dynamic_preferences.global.section", kwargs={"section": 'user'})
        response = self.client.get(url)
        self.assertEqual(len(response.context['form'].fields), 3)

    def test_preference_are_updated_on_form_submission(self):
        self.client.login(username='admin', password="test")
        url = reverse(
            "dynamic_preferences.global.section", kwargs={"section": 'user'})
        response = self.client.post(url, {'user__max_users': 95, 'user__registration_allowed': True,
                                          "user__items_per_page": 12})
        self.assertEqual(GlobalPreferenceModel.objects.get(
            section="user", name="max_users").value, 95)
        self.assertEqual(GlobalPreferenceModel.objects.get(
            section="user", name="registration_allowed").value, True)
        self.assertEqual(GlobalPreferenceModel.objects.get(
            section="user", name="items_per_page").value, 12)

    def test_user_preference_form_is_bound_with_current_user(self):
        self.client.login(username='henri', password="test")
        self.assertEqual(UserPreferenceModel.objects.get_or_create(
            instance=self.henri, section="misc", name='favourite_colour')[0].value, 'Green')
        self.assertEqual(UserPreferenceModel.objects.get_or_create(
            instance=self.henri, section="misc", name='is_zombie')[0].value, True)

        url = reverse(
            "dynamic_preferences.user.section", kwargs={'section': 'misc'})
        response = self.client.post(
            url, {'misc__favourite_colour': 'Purple', 'misc__is_zombie': False})

        self.assertEqual(self.henri.preferences['misc__favourite_colour'], 'Purple')
        self.assertEqual(self.henri.preferences['misc__is_zombie'], False)

    def test_template_gets_global_preferences_via_template_processor(self):
        global_preferences = global_preferences_registry.manager()
        url = reverse("dynamic_preferences.test.templateview")
        response = self.client.get(url)
        self.assertEqual(
            response.context['global_preferences'], global_preferences.all())
