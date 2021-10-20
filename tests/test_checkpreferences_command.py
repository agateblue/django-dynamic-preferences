from io import StringIO

from django.core.cache import caches
from django.core.management import call_command
from django.test import TestCase


class BaseTest(object):

    def tearDown(self):
        caches["default"].clear()


class TestCheckPreferencesCommand(BaseTest, TestCase):
    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "checkpreferences",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue().strip()

    def test_dry_run(self):
        out = self.call_command(verbosity=0)
        expected_output = "\n".join([
            "Creating missing global preferences...",
            "Deleted 0 global preferences",
            "Deleted 0 GlobalPreferenceModel preferences",
            "Deleted 0 UserPreferenceModel preferences",
            "Creating missing preferences for User model...",
        ])
        self.assertEqual(out, expected_output)
