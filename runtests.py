#!/usr/bin/env python
from django.conf import settings, global_settings as default_settings
from django.core.management import call_command
from os.path import dirname, realpath
import django
import sys
import os
from dynamic_preferences.registries import autodiscover
# Give feedback on used versions
sys.stderr.write('Using Python version {0} from {1}\n'.format(sys.version[:5], sys.executable))
sys.stderr.write('Using Django version {0} from {1}\n'.format(
    django.get_version(),
    os.path.dirname(os.path.abspath(django.__file__)))
)


# Detect location and available modules
module_root = dirname(realpath(__file__))

# Inline settings file
settings.configure(
    DEBUG = False, # will be False anyway by DjangoTestRunner.
    TEMPLATE_DEBUG = False,
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    },
    TEMPLATE_CONTEXT_PROCESSORS = default_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'django.core.context_processors.request',
        'dynamic_preferences.processors.global_preferences',
        'dynamic_preferences.processors.user_preferences',
    ),
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.sites',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'dynamic_preferences',
    ),
    ROOT_URLCONF = 'dynamic_preferences.urls',
    SITE_ID = 1,    
    STATIC_URL = "/static/",
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ),

    DYNAMIC_PREFERENCES_USE_TEST_PREFERENCES=True,
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console':{
                'level':'DEBUG',
                'class':'logging.StreamHandler',
                'formatter': 'simple'
            },
        },
        'loggers': {
            'django.request':{
                'handlers': ['console'],
                'propagate': True,
                'level': 'DEBUG',
            },
        },
    },
    TESTING=True
)
call_command('syncdb', verbosity=1, interactive=False)
autodiscover()


# ---- app start
verbosity = 2 if '-v' in sys.argv else 1

from django.test.utils import get_runner
TestRunner = get_runner(settings) # DjangoTestSuiteRunner
runner = TestRunner(verbosity=verbosity, interactive=True, failfast=False)
failures = runner.run_tests(['dynamic_preferences'])

if failures:
    sys.exit(bool(failures))