from __future__ import unicode_literals
from django.test import LiveServerTestCase, TestCase
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.core.cache import caches
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from dynamic_preferences.registries import (
    global_preferences_registry as registry
)
from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.forms import global_preference_form_builder

from .test_app.models import BlogEntry


class BaseTest(object):

    def tearDown(self):
        caches['default'].clear()


class TestGlobalPreferences(BaseTest, TestCase):

    def setUp(self):
        self.test_user = User(
            username="test", password="test", email="test@test.com")
        self.test_user.save()

    def test_preference_model_manager_to_dict(self):
        manager = registry.manager()
        call_command('checkpreferences', verbosity=1, interactive=False)
        expected = {
            u'test__TestGlobal1': u'default value',
            u'test__TestGlobal2': False,
            u'test__TestGlobal3': False,
            u'no_section': False,
            u'user__max_users': 100,
            u'user__items_per_page': 25,
            u'blog__featured_entry': None,
            u'blog__logo': None,
            u'user__registration_allowed': False}
        self.assertDictEqual(manager.all(), expected)


class TestViews(BaseTest, LiveServerTestCase):

    def setUp(self):
        self.admin = User(
            username="admin",
            email="admin@admin.com",
            is_superuser=True,
            is_staff=True)
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
        self.assertEqual(len(response.context['form'].fields), 9)
        self.assertEqual(
            response.context['registry'], registry)

    def test_formview_includes_section_in_context(self):
        url = reverse(
            "dynamic_preferences.global.section", kwargs={"section": 'user'})
        self.client.login(username='admin', password="test")
        response = self.client.get(url)
        self.assertEqual(
            response.context['section'], registry.section_objects['user'])

    def test_formview_with_bad_section_returns_404(self):
        url = reverse(
            "dynamic_preferences.global.section", kwargs={"section": 'nope'})
        self.client.login(username='admin', password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_global_preference_filters_by_section(self):
        self.client.login(username='admin', password="test")
        url = reverse(
            "dynamic_preferences.global.section", kwargs={"section": 'user'})
        response = self.client.get(url)
        self.assertEqual(len(response.context['form'].fields), 3)

    def test_preference_are_updated_on_form_submission(self):
        blog_entry = BlogEntry.objects.create(title='test', content='test')
        self.client.login(username='admin', password="test")
        url = reverse("dynamic_preferences.global")
        data = {
            'user__max_users': 67,
            'user__registration_allowed': True,
            "user__items_per_page": 12,
            'test__TestGlobal1': 'new value',
            'test__TestGlobal2': True,
            'test__TestGlobal3': True,
            'no_section': True,
            'blog__featured_entry': blog_entry.pk,
            'blog__logo': None,
        }
        response = self.client.post(url, data)
        for key, expected_value in data.items():
            try:
                section, name = key.split('__')
            except ValueError:
                section, name = (None, key)

            p = GlobalPreferenceModel.objects.get(name=name, section=section)
            if name == 'featured_entry':
                expected_value = blog_entry
            self.assertEqual(p.value, expected_value)

    def test_preference_are_updated_on_form_submission_by_section(self):
        self.client.login(username='admin', password="test")
        url = reverse(
            "dynamic_preferences.global.section", kwargs={"section": 'user'})
        response = self.client.post(
            url,
            {'user__max_users': 95,
             'user__registration_allowed': True,
             'user__items_per_page': 12})
        self.assertEqual(GlobalPreferenceModel.objects.get(
            section="user", name="max_users").value, 95)
        self.assertEqual(GlobalPreferenceModel.objects.get(
            section="user", name="registration_allowed").value, True)
        self.assertEqual(GlobalPreferenceModel.objects.get(
            section="user", name="items_per_page").value, 12)

    def test_template_gets_global_preferences_via_template_processor(self):
        global_preferences = registry.manager()
        url = reverse("dynamic_preferences.test.templateview")
        response = self.client.get(url)
        self.assertEqual(
            response.context['global_preferences'], global_preferences.all())

    def test_file_preference(self):

        blog_entry = BlogEntry.objects.create(title='Hello', content='World')
        content = b"hello"
        logo = SimpleUploadedFile(
            "logo.png", content, content_type="image/png")
        self.client.login(username='admin', password="test")
        url = reverse(
            "dynamic_preferences.global.section", kwargs={"section": 'blog'})
        response = self.client.post(
            url,
            {'blog__featured_entry': blog_entry.pk,
             'blog__logo': logo})
        self.assertEqual(GlobalPreferenceModel.objects.get(
            section="blog", name="featured_entry").value, blog_entry)
        self.assertEqual(GlobalPreferenceModel.objects.get(
            section="blog", name="logo").value.read(), content)
