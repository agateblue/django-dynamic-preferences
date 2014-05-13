from django.conf import settings
from os.path import abspath, dirname, join

DJANGO_ROOT = dirname(dirname(abspath(__file__)))
PROJECT_PATH = join(DJANGO_ROOT, "dynamic_preferences")

settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'NAME': "dynamic_preferences.sq3",
            'ENGINE': 'django.db.backends.sqlite3',
        }
    },
    INSTALLED_APPS=('django.contrib.auth',
                   'django.contrib.sites',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.admin',
                  "debug_toolbar",
                  'django.contrib.staticfiles',
                  'dynamic_preferences',),
    SITE_ID=1,
    ROOT_URLCONF='dynamic_preferences.urls',
    STATIC_ROOT=join(PROJECT_PATH, "static"),
    STATIC_URL="/static/",
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
)
