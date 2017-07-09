from __future__ import unicode_literals
from django.test import TestCase
from django.core.cache import caches
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

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

    def test_do_not_restore_default_when_calling_all(self):
        manager = registry.manager()

        new_value = 'test_new_value'
        manager['test__TestGlobal1'] = new_value
        self.assertEqual(manager['test__TestGlobal1'], new_value)
        caches['default'].clear()
        manager.all()
        caches['default'].clear()
        self.assertEqual(manager['test__TestGlobal1'], new_value)
        self.assertEqual(manager.all()['test__TestGlobal1'], new_value)

    def test_invalidates_cache_when_saving_database_preference(self):
        manager = registry.manager()
        caches['default'].clear()
        new_value = 'test_new_value'
        key = manager.get_cache_key('test', 'TestGlobal1')
        manager['test__TestGlobal1'] = new_value

        pref = manager.get_db_pref(section='test', name='TestGlobal1')
        self.assertEqual(pref.raw_value, new_value)
        self.assertEqual(manager.cache.get(key), new_value)

        pref.raw_value = 'reset'
        pref.save()

        self.assertEqual(manager.cache.get(key), 'reset')

    def test_invalidates_cache_when_saving_from_admin(self):
        admin = User(
            username="admin",
            email="admin@admin.com",
            is_superuser=True,
            is_staff=True)
        admin.set_password('test')
        admin.save()
        self.client.login(username='admin', password="test")

        manager = registry.manager()
        pref = manager.get_db_pref(section='test', name='TestGlobal1')
        url = reverse(
            'admin:dynamic_preferences_globalpreferencemodel_change',
            args=(pref.id,)
        )
        key = manager.get_cache_key('test', 'TestGlobal1')

        response = self.client.post(url, {'raw_value': 'reset1'})

        self.assertEqual(manager.cache.get(key), 'reset1')
        self.assertEqual(manager.all()['test__TestGlobal1'], 'reset1')

        response = self.client.post(url, {'raw_value': 'reset2'})

        self.assertEqual(manager.cache.get(key), 'reset2')
        self.assertEqual(manager.all()['test__TestGlobal1'], 'reset2')
