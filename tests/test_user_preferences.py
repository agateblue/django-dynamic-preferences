from __future__ import unicode_literals
import json

from django.test import LiveServerTestCase, TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import caches
from django.db import IntegrityError

from dynamic_preferences.users.registries import (
    user_preferences_registry as registry)
from dynamic_preferences.users.models import UserPreferenceModel
from dynamic_preferences.users import serializers
from dynamic_preferences.managers import PreferencesManager
from dynamic_preferences.users.forms import user_preference_form_builder
from .test_app.dynamic_preferences_registry import *


class BaseTest(object):

    def tearDown(self):
        caches['default'].clear()


class TestModels(BaseTest, TestCase):

    def test_adding_user_create_default_preferences(self):

        u = User(username="post_create")
        u.save()

        self.assertEqual(
            len(u.preferences), len(registry.preferences()))


class TestDynamicPreferences(BaseTest, TestCase):

    def setUp(self):

        self.test_user = User(
            username="test", password="test", email="test@test.com")
        self.test_user.save()

    def test_manager_is_attached_to_each_referenced_instance(self):
        self.assertTrue(isinstance(
            self.test_user.preferences, PreferencesManager))

    def test_preference_is_saved_to_database(self):

        self.test_user.preferences['test__TestUserPref1'] = 'new test value'

        test_user_pref1 = UserPreferenceModel.objects.get(
            section="test", name="TestUserPref1", instance=self.test_user)

        self.assertEqual(
            self.test_user.preferences['test__TestUserPref1'],
            "new test value")

    def test_per_instance_preference_stay_unique_in_db(self):

        self.test_user.preferences['test__TestUserPref1'] = 'new value'

        duplicate = UserPreferenceModel(
            section="test", name="TestUserPref1", instance=self.test_user)

        with self.assertRaises(IntegrityError):
            duplicate.save()

    def test_preference_value_set_to_default(self):

        pref = registry.get("TestUserPref1", "test")

        value = self.test_user.preferences['test__TestUserPref1']
        self.assertEqual(pref.default, value)
        instance = UserPreferenceModel.objects.get(
            section="test", name="TestUserPref1", instance=self.test_user)

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


class TestViews(BaseTest, LiveServerTestCase):

    def setUp(self):
        self.henri = User(
            username="henri",
            password="test",
            email="henri@henri.com")
        self.henri.set_password('test')
        self.henri.save()

        self.admin = User(
            username="admin",
            email="admin@admin.com",
            is_superuser=True,
            is_staff=True)
        self.admin.set_password('test')
        self.admin.save()

    def test_can_build_user_preference_form_from_sections(self):
        form = user_preference_form_builder(
            instance=self.admin, section='test')()

        self.assertEqual(len(form.fields), 4)

    def test_user_preference_form_is_bound_with_current_user(self):
        self.client.login(username='henri', password="test")
        self.assertEqual(
            UserPreferenceModel.objects.get_or_create(
                instance=self.henri,
                section="misc",
                name='favourite_colour')[0].value,
            'Green')
        self.assertTrue(
            UserPreferenceModel.objects.get_or_create(
                instance=self.henri,
                section="misc",
                name='is_zombie')[0].value)

        url = reverse(
            "dynamic_preferences.user.section", kwargs={'section': 'misc'})
        response = self.client.post(
            url, {
                'misc__favourite_colour':
                'Purple',
                'misc__is_zombie': False})

        self.assertEqual(
            self.henri.preferences['misc__favourite_colour'], 'Purple')
        self.assertEqual(
            self.henri.preferences['misc__is_zombie'], False)


class TestViewSets(BaseTest, TestCase):
    def setUp(self):
        self.user = User(
            username="user",
            email="user@user.com",
            is_superuser=True,
            is_staff=True)
        self.user.set_password('test')
        self.user.save()

    def test_preference_list_requires_authentication(self):
        url = reverse('api:user-list')

        # anonymous
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_can_list_preferences(self):
        manager = registry.manager(instance=self.user)
        url = reverse('api:user-list')
        self.client.login(username='user', password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(payload), len(registry.preferences()))

        for e in payload:
            pref = manager.get_db_pref(section=e['section'], name=e['name'])
            serializer = serializers.UserPreferenceSerializer(pref)
            self.assertEqual(pref.preference.identifier(), e['identifier'])

    def test_can_detail_preference(self):
        manager = registry.manager(instance=self.user)
        pref = manager.get_db_pref(section='user', name='favorite_vegetable')
        url = reverse(
            'api:user-detail',
            kwargs={'pk': pref.preference.identifier()})
        self.client.login(username='user', password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content.decode('utf-8'))
        self.assertEqual(pref.preference.identifier(), payload['identifier'])
        self.assertEqual(pref.value, payload['value'])

    def test_can_update_preference(self):
        manager = registry.manager(instance=self.user)
        pref = manager.get_db_pref(section='user', name='favorite_vegetable')
        url = reverse(
            'api:user-detail',
            kwargs={'pk': pref.preference.identifier()})
        self.client.login(username='user', password="test")
        response = self.client.patch(
            url, json.dumps({'value': 'P'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        pref = manager.get_db_pref(section='user', name='favorite_vegetable')

        self.assertEqual(pref.value, 'P')

    def test_can_update_multiple_preferences(self):
        manager = registry.manager(instance=self.user)
        pref = manager.get_db_pref(section='user', name='favorite_vegetable')
        url = reverse('api:user-bulk')
        self.client.login(username='user', password="test")
        payload = {
            'user__favorite_vegetable': 'C',
            'misc__favourite_colour': 'Blue',
        }
        response = self.client.post(
            url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        pref1 = manager.get_db_pref(section='user', name='favorite_vegetable')
        pref2 = manager.get_db_pref(
            section='misc', name='favourite_colour')

        self.assertEqual(pref1.value, 'C')
        self.assertEqual(pref2.value, 'Blue')

    def test_update_preference_returns_validation_error(self):
        manager = registry.manager(instance=self.user)
        pref = manager.get_db_pref(section='user', name='favorite_vegetable')
        url = reverse(
            'api:user-detail',
            kwargs={'pk': pref.preference.identifier()})
        self.client.login(username='user', password="test")
        response = self.client.patch(
            url, json.dumps({'value': 'Z'}), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        payload = json.loads(response.content.decode('utf-8'))

        self.assertIn('valid choice', payload['value'][0])

    def test_update_multiple_preferences_with_validation_errors_rollback(self):
        manager = registry.manager(instance=self.user)
        pref = manager.get_db_pref(section='user', name='favorite_vegetable')
        url = reverse('api:user-bulk')
        self.client.login(username='user', password="test")
        payload = {
            'user__favorite_vegetable': 'Z',
            'misc__favourite_colour': 'Blue',
        }
        response = self.client.post(
            url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        errors = json.loads(response.content.decode('utf-8'))
        self.assertIn(
            'valid choice',
            errors[pref.preference.identifier()]['value'][0])

        pref1 = manager.get_db_pref(section='user', name='favorite_vegetable')
        pref2 = manager.get_db_pref(
            section='misc', name='favourite_colour')

        self.assertEqual(pref1.value, pref1.preference.default)
        self.assertEqual(pref2.value, pref2.preference.default)
