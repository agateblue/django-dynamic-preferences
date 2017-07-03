from __future__ import unicode_literals
import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import caches
from dynamic_preferences.registries import (
    global_preferences_registry as registry
)
from dynamic_preferences.users.registries import (
    user_preferences_registry as user_registry
)
from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.forms import global_preference_form_builder
from dynamic_preferences.api import serializers
from dynamic_preferences.users.serializers import UserPreferenceSerializer
from .test_app.models import BlogEntry


class BaseTest(object):

    def tearDown(self):
        caches['default'].clear()


class TestSerializers(BaseTest, TestCase):

    def test_can_serialize_preference(self):
        manager = registry.manager()
        pref = manager.get_db_pref(section='user', name='max_users')

        serializer = serializers.GlobalPreferenceSerializer(pref)
        data = serializer.data

        self.assertEqual(
            data['default'], pref.preference.api_repr(pref.preference.default))
        self.assertEqual(
            data['value'], pref.preference.api_repr(pref.value))
        self.assertEqual(data['identifier'], pref.preference.identifier())
        self.assertEqual(data['section'], pref.section)
        self.assertEqual(data['name'], pref.name)
        self.assertEqual(data['verbose_name'], pref.preference.verbose_name)
        self.assertEqual(data['help_text'], pref.preference.help_text)
        self.assertEqual(data['field']['class'], 'IntegerField')
        self.assertEqual(data['field']['input_type'], 'number')
        self.assertEqual(data['field']['widget']['class'], 'NumberInput')

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

    def test_serializer_includes_additional_data_if_any(self):
        user = User(
            username="user",
            email="user@user.com")
        user.set_password('test')
        user.save()

        manager = user_registry.manager(instance=user)
        pref = manager.get_db_pref(
            section='user', name='favorite_vegetable')

        serializer = UserPreferenceSerializer(pref)
        self.assertEqual(
            serializer.data['additional_data']['choices'],
            pref.preference.choices)


class TestViewSets(BaseTest, TestCase):
    def setUp(self):
        self.admin = User(
            username="admin",
            email="admin@admin.com",
            is_superuser=True,
            is_staff=True)
        self.admin.set_password('test')
        self.admin.save()

    def test_global_preference_list_requires_permission(self):
        url = reverse('api:global-list')

        # anonymous
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # not authorized
        user = User(
            username="user",
            email="user@user.com")
        user.set_password('test')
        user.save()

        self.client.login(username='test', password='test')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_can_list_preferences(self):
        manager = registry.manager()
        url = reverse('api:global-list')
        self.client.login(username='admin', password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(payload), len(registry.preferences()))

        for e in payload:
            pref = manager.get_db_pref(section=e['section'], name=e['name'])
            serializer = serializers.GlobalPreferenceSerializer(pref)
            self.assertEqual(pref.preference.identifier(), e['identifier'])

    def test_can_detail_preference(self):
        manager = registry.manager()
        pref = manager.get_db_pref(section='user', name='max_users')
        url = reverse(
            'api:global-detail',
            kwargs={'pk': pref.preference.identifier()})
        self.client.login(username='admin', password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content.decode('utf-8'))
        self.assertEqual(pref.preference.identifier(), payload['identifier'])
        self.assertEqual(pref.value, payload['value'])

    def test_can_update_preference(self):
        manager = registry.manager()
        pref = manager.get_db_pref(section='user', name='max_users')
        url = reverse(
            'api:global-detail',
            kwargs={'pk': pref.preference.identifier()})
        self.client.login(username='admin', password="test")
        response = self.client.patch(
            url, json.dumps({'value': 16}), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        pref = manager.get_db_pref(section='user', name='max_users')

        self.assertEqual(pref.value, 16)

    def test_can_update_multiple_preferences(self):
        manager = registry.manager()
        pref = manager.get_db_pref(section='user', name='max_users')
        url = reverse('api:global-bulk')
        self.client.login(username='admin', password="test")
        payload = {
            'user__max_users': 16,
            'user__registration_allowed': True,
        }
        response = self.client.post(
            url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        pref1 = manager.get_db_pref(section='user', name='max_users')
        pref2 = manager.get_db_pref(
            section='user', name='registration_allowed')

        self.assertEqual(pref1.value, 16)
        self.assertEqual(pref2.value, True)

    def test_update_preference_returns_validation_error(self):
        manager = registry.manager()
        pref = manager.get_db_pref(section='user', name='max_users')
        url = reverse(
            'api:global-detail',
            kwargs={'pk': pref.preference.identifier()})
        self.client.login(username='admin', password="test")
        response = self.client.patch(
            url, json.dumps({'value': 1001}), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        payload = json.loads(response.content.decode('utf-8'))

        self.assertEqual(payload['value'], ['Wrong value!'])

    def test_update_multiple_preferences_with_validation_errors_rollback(self):
        manager = registry.manager()
        pref = manager.get_db_pref(section='user', name='max_users')
        url = reverse('api:global-bulk')
        self.client.login(username='admin', password="test")
        payload = {
            'user__max_users': 1001,
            'user__registration_allowed': True,
        }
        response = self.client.post(
            url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        errors = json.loads(response.content.decode('utf-8'))
        self.assertEqual(
            errors[pref.preference.identifier()]['value'], ['Wrong value!'])

        pref1 = manager.get_db_pref(section='user', name='max_users')
        pref2 = manager.get_db_pref(
            section='user', name='registration_allowed')

        self.assertEqual(pref1.value, pref1.preference.default)
        self.assertEqual(pref2.value, pref2.preference.default)
