from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import caches

from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.users.models import UserPreferenceModel


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

        self.assertFalse(global_preferences['user__registration_allowed'])

        global_preferences['user__registration_allowed'] = True

        self.assertTrue(global_preferences['user__registration_allowed'])
        self.assertTrue(
            GlobalPreferenceModel.objects.get(
                section="user", name="registration_allowed").value)

        self.assertEqual(
            self.henri.preferences['misc__favourite_colour'],
            'Green')

        self.henri.preferences['misc__favourite_colour'] = 'Blue'

        self.assertEqual(
            self.henri.preferences['misc__favourite_colour'],
            'Blue')

        self.assertEqual(
            UserPreferenceModel.objects.get(
                section="misc",
                name="favourite_colour",
                instance=self.henri).value,
            'Blue')
