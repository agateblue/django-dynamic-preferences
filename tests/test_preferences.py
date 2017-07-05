from __future__ import unicode_literals
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.core.cache import caches

from dynamic_preferences.registries import (
    MissingPreference,
    global_preferences_registry)
from dynamic_preferences import preferences, exceptions
from dynamic_preferences.types import IntegerPreference

from .test_app import dynamic_preferences_registry as prefs
from .test_app.models import BlogEntry


class BaseTest(object):

    def tearDown(self):
        caches['default'].clear()


class TestRegistry(BaseTest, TestCase):

    def test_can_retrieve_preference_using_dotted_notation(self):
        registration_allowed = global_preferences_registry.get(
            name="registration_allowed", section="user")
        dotted_result = global_preferences_registry.get(
            "user__registration_allowed")
        self.assertEqual(registration_allowed, dotted_result)

    def test_can_register_and_retrieve_preference_with_section_none(self):
        no_section_pref = global_preferences_registry.get(name="no_section")
        self.assertEqual(no_section_pref.section, preferences.EMPTY_SECTION)


class TestPreferences(BaseTest, TestCase):

    def test_cannot_instanciate_preference_or_section_with_invalid_name(self):

        invalid_names = ['with space', 'with__separator', 'with-hyphen']

        for n in invalid_names:
            with self.assertRaises(ValueError):
                preferences.Section(n)
            with self.assertRaises(ValueError):
                class P(IntegerPreference):
                    name = n
                P()

    def test_preference_order_match_register_call(self):
        expected = [
            'registration_allowed',
            'max_users',
            'items_per_page',
            'featured_entry',
        ]
        self.assertEqual(
            [p.name for p in global_preferences_registry.preferences()][:4],
            expected)

    def test_preferences_manager_get(self):
        global_preferences = global_preferences_registry.manager()
        self.assertEqual(global_preferences['no_section'], False)

    def test_preferences_manager_set(self):
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

    @override_settings(DYNAMIC_PREFERENCES={'ENABLE_CACHE': False})
    def test_can_bypass_cache_in_get(self):
        manager = global_preferences_registry.manager()
        manager['no_section']
        with self.assertNumQueries(3):
            manager['no_section']
            manager['no_section']
            manager['no_section']

    @override_settings(DYNAMIC_PREFERENCES={'ENABLE_CACHE': False}, DEBUG=True)
    def test_can_bypass_cache_in_get_all(self):
        from django.db import connection
        manager = global_preferences_registry.manager()

        queries_before = len(connection.queries)
        manager.all()
        manager_queries = len(connection.queries) - queries_before

        manager.all()
        self.assertGreater(len(connection.queries), manager_queries)

    def test_can_cache_all_preferences(self):
        blog_entry = BlogEntry.objects.create(title='test', content='test')
        manager = global_preferences_registry.manager()
        manager.all()
        with self.assertNumQueries(3):
            # one request each time we retrieve the blog entry
            manager.all()
            manager.all()
            manager.all()

    def test_preferences_manager_by_name(self):
        manager = global_preferences_registry.manager()
        self.assertEqual(
            manager.by_name()['max_users'], manager['user__max_users'])
        self.assertEqual(len(manager.all()), len(manager.by_name()))

    def test_cache_invalidate_on_save(self):
        manager = global_preferences_registry.manager()
        model_instance = manager.create_db_pref(
            section=None, name='no_section', value=False)

        with self.assertNumQueries(0):
            assert not manager['no_section']
            manager['no_section']

        model_instance.value = True
        model_instance.save()

        with self.assertNumQueries(0):
            assert manager['no_section']
            manager['no_section']

    @override_settings(DYNAMIC_PREFERENCES={'ENABLE_CACHE': False})
    def test_can_get_single_pref_with_cache_disabled(self):
        manager = global_preferences_registry.manager()
        v = manager['no_section']
        self.assertIsInstance(v, bool)

    def test_can_get_single_pref_bypassing_cache(self):
        manager = global_preferences_registry.manager()
        v = manager.get('no_section', no_cache=True)
        self.assertIsInstance(v, bool)

    def test_do_not_crash_if_preference_is_missing_in_registry(self):
        """see #41"""
        manager = global_preferences_registry.manager()
        instance = manager.create_db_pref(
            section=None, name='bad_pref', value='something')

        self.assertTrue(
            isinstance(instance.preference, MissingPreference))

        self.assertEqual(instance.preference.section, None)
        self.assertEqual(instance.preference.name, 'bad_pref')
        self.assertEqual(instance.value, 'something')

    def test_can_get_to_string_notation(self):
        pref = global_preferences_registry.get('user__registration_allowed')

        self.assertEqual(pref.identifier(), 'user__registration_allowed')

    def test_preference_requires_default_value(self):
        with self.assertRaises(exceptions.MissingDefault):
            preference = prefs.NoDefault()
