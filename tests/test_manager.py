from __future__ import unicode_literals
from django.test import TestCase
from django.core.cache import caches

from dynamic_preferences.registries import (
    global_preferences_registry as registry
)
from dynamic_preferences.models import GlobalPreferenceModel


class BaseTest(object):

    def tearDown(self):
        caches['default'].clear()


class TestPreferences(BaseTest, TestCase):

    def test_can_get_preferences_objects_from_manager(self):
        manager = registry.manager()
        cached_prefs = dict(manager.all())
        qs = manager.queryset

        self.assertEqual(
            len(qs),
            len(cached_prefs)
        )

        self.assertEqual(
            list(qs),
            list(GlobalPreferenceModel.objects.all())
        )

    def test_can_get_db_pref_from_manager(self):
        manager = registry.manager()
        manager.queryset.delete()
        pref = manager.get_db_pref(section='test', name='TestGlobal1')

        self.assertEqual(pref.section, 'test')
        self.assertEqual(pref.name, 'TestGlobal1')
        self.assertEqual(
            pref.raw_value, registry.get('test__TestGlobal1').default)
