import decimal

from django.test import TestCase
from django.db.models import signals
from django.test.utils import override_settings
from django.core.cache import caches
from django import forms

from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences import types

from .test_app.models import BlogEntry


class BaseTest(object):

    def tearDown(self):
        caches['default'].clear()


class TestTypes(BaseTest, TestCase):
    @override_settings(DYNAMIC_PREFERENCES={'VALIDATE_NAMES': False})
    def test_default_accepts_callable(self):

        class P(types.IntPreference):
            def get_default(self):
                return 4

        self.assertEqual(P().get('default'), 4)

    @override_settings(DYNAMIC_PREFERENCES={'VALIDATE_NAMES': False})
    def test_getter(self):
        class PNoGetter(types.IntPreference):
            default = 1
            help_text = 'Hello'

        class PGetter(types.IntPreference):
            def get_default(self):
                return 1

            def get_help_text(self):
                return 'Hello'

        p_no_getter = PNoGetter()
        p_getter = PGetter()
        for attribute, expected in [('default', 1), ('help_text', 'Hello')]:
            self.assertEqual(p_no_getter.get(attribute), expected)
            self.assertEqual(p_getter.get(attribute), expected)

    @override_settings(DYNAMIC_PREFERENCES={'VALIDATE_NAMES': False})
    def test_field(self):
        class P(types.IntPreference):
            default = 1
            verbose_name = 'P'
        p = P()

        self.assertEqual(p.field.initial, 1)
        self.assertEqual(p.field.label, 'P')
        self.assertEqual(p.field.__class__, forms.IntegerField)

    @override_settings(DYNAMIC_PREFERENCES={'VALIDATE_NAMES': False})
    def test_boolean_field_class_instantiation(self):

        class P(types.BooleanPreference):
            default = False
        preference = P()
        self.assertEqual(preference.field.initial, False)

    @override_settings(DYNAMIC_PREFERENCES={'VALIDATE_NAMES': False})
    def test_char_field_class_instantiation(self):
        class P(types.StringPreference):
            default = "hello world!"
        preference = P()

        self.assertEqual(preference.field.initial, "hello world!")

    @override_settings(DYNAMIC_PREFERENCES={'VALIDATE_NAMES': False})
    def test_longstring_preference_widget(self):
        class P(types.LongStringPreference):
            default = "hello world!"
        preference = P()

        self.assertTrue(isinstance(preference.field.widget, forms.Textarea))

    @override_settings(DYNAMIC_PREFERENCES={'VALIDATE_NAMES': False})
    def test_decimal_preference(self):
        class P(types.DecimalPreference):
            default = decimal.Decimal('2.5')
        preference = P()

        self.assertEqual(preference.field.initial, decimal.Decimal('2.5'))

    @override_settings(DYNAMIC_PREFERENCES={'VALIDATE_NAMES': False})
    def test_float_preference(self):
        class P(types.FloatPreference):
            default = 0.35
        preference = P()

        self.assertEqual(preference.field.initial, 0.35)
        self.assertNotEqual(preference.field.initial, 0.3)
        self.assertNotEqual(preference.field.initial, 0.3001)


class TestModelChoicePreference(BaseTest, TestCase):

    def setUp(self):
        super(TestModelChoicePreference, self).setUp()
        self.blog_entry = BlogEntry(title='Hello', content='World')
        self.blog_entry.save()

    def test_model_choice_preference(self):
        global_preferences = global_preferences_registry.manager()
        global_preferences['blog__featured_entry'] = self.blog_entry

        in_db = GlobalPreferenceModel.objects.get(
            section='blog', name='featured_entry')
        self.assertEqual(in_db.value, self.blog_entry)
        self.assertEqual(in_db.raw_value, str(self.blog_entry.pk))

    def test_deleting_model_also_delete_preference(self):
        global_preferences = global_preferences_registry.manager()
        global_preferences['blog__featured_entry'] = self.blog_entry

        self.assertGreater(len(signals.pre_delete.receivers), 0)

        self.blog_entry.delete()

        with self.assertRaises(GlobalPreferenceModel.DoesNotExist):
            GlobalPreferenceModel.objects.get(
                section='blog', name='featured_entry')
