from __future__ import unicode_literals
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.cache import caches
from django.contrib.auth.models import User

from dynamic_preferences.registries import (
    global_preferences_registry as registry
)
from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.forms import global_preference_form_builder
from dynamic_preferences.api import serializers

from .test_app.models import BlogEntry


class BaseTest(object):

    def tearDown(self):
        caches['default'].clear()


class TestGlobalPreferences(BaseTest, TestCase):

    def test_can_serialize_preference(self):
        manager = registry.manager()
        pref = manager.get_db_pref(section='user', name='max_users')

        serializer = serializers.GlobalPreferenceSerializer(pref)
        data = serializer.data

        self.assertEqual(
            data['default'], pref.preference.api_repr(pref.preference.default))
        self.assertEqual(
            data['value'], pref.preference.api_repr(pref.value))
        self.assertEqual(data['section'], pref.section)
        self.assertEqual(data['name'], pref.name)
        self.assertEqual(data['verbose_name'], pref.preference.verbose_name)
        self.assertEqual(data['help_text'], pref.preference.help_text)

    def test_can_change_preference_value_using_serializer(self):
        manager = registry.manager()
        pref = manager.get_db_pref(section='user', name='max_users')
        data = {'value': 666}
        serializer = serializers.GlobalPreferenceSerializer(pref, data=data)

        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)

        serializer.save()
        pref = manager.get_db_pref(section='user', name='max_users')

        self.assertEqual(pref.value, data['value'])

    def test_serializer_also_uses_custom_clean_method(self):
        manager = registry.manager()
        pref = manager.get_db_pref(section='user', name='max_users')

        # will fail because of preference cleaning
        data = {'value': 1001}
        serializer = serializers.GlobalPreferenceSerializer(pref, data=data)

        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertIn('value', serializer.errors)
