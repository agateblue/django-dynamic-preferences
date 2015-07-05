import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from django.conf import settings
    from django.conf import global_settings
    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
            }
        },
        ROOT_URLCONF='tests.urls',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.sites',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.admin',
            'dynamic_preferences',
            'tests.test_app'
        ],
        SITE_ID=1,
        STATIC_URL='/static/',
        NOSE_ARGS=['-s'],
        MIDDLEWARE_CLASSES= (
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ),
        TEMPLATE_CONTEXT_PROCESSORS=global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
            'django.core.context_processors.request',
            'dynamic_preferences.processors.global_preferences',
        ),
        DYNAMIC_PREFERENCES_USE_TEST_PREFERENCES=True,
        TESTING=True,
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake',
            }
        },
    )
    try:
        import django
        setup = django.setup
    except AttributeError:
        pass
    else:
        setup()

    from django_nose import NoseTestSuiteRunner
except ImportError:
    import traceback
    traceback.print_exc()
    raise ImportError("To fix this error, run: pip install -r requirements-test.txt")


def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    # Run tests
    test_runner = NoseTestSuiteRunner(verbosity=1)

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(failures)


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
