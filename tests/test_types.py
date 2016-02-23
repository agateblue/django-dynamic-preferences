from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.registries import user_preferences_registry, global_preferences_registry
from django.db.models import signals

from .tests import BaseTest, TestCase
from .test_app.models import BlogEntry
class TestModelChoicePreference(BaseTest, TestCase):

    def setUp(self):
        super(TestModelChoicePreference, self).setUp()
        self.blog_entry = BlogEntry(title='Hello', content='World')
        self.blog_entry.save()

    def test_model_choice_preference(self):
        global_preferences = global_preferences_registry.manager()
        global_preferences['blog__featured_entry'] = self.blog_entry

        in_db = GlobalPreferenceModel.objects.get(section='blog', name='featured_entry')
        self.assertEqual(in_db.value, self.blog_entry)
        self.assertEqual(in_db.raw_value, str(self.blog_entry.pk))

    def test_deleting_model_also_delete_preference(self):
        global_preferences = global_preferences_registry.manager()
        global_preferences['blog__featured_entry'] = self.blog_entry

        self.assertGreater(len(signals.pre_delete.receivers), 0)

        self.blog_entry.delete()

        with self.assertRaises(GlobalPreferenceModel.DoesNotExist):
            GlobalPreferenceModel.objects.get(section='blog', name='featured_entry')
