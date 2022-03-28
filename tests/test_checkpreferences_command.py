from io import StringIO

from django.core.cache import caches
from django.core.management import call_command
from django.test import TestCase


def call(*args, **kwargs):
    out = StringIO()
    call_command(
        "checkpreferences",
        *args,
        stdout=out,
        stderr=StringIO(),
        **kwargs,
    )
    return out.getvalue().strip()


def test_dry_run(db):
    out = call(verbosity=0)
    expected_output = "\n".join(
        [
            "Creating missing global preferences...",
            "Deleted 0 global preferences",
            "Deleted 0 GlobalPreferenceModel preferences",
            "Deleted 0 UserPreferenceModel preferences",
            "Creating missing preferences for User model...",
        ]
    )
    assert out == expected_output


def test_skip_create(db):
    out = call("--skip_create", verbosity=0)
    expected_output = "\n".join(
        [
            "Deleted 0 global preferences",
            "Deleted 0 GlobalPreferenceModel preferences",
            "Deleted 0 UserPreferenceModel preferences",
        ]
    )
    assert out == expected_output
