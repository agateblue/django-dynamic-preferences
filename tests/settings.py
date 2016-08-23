
DEBUG = True
USE_TZ = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    }
}
ROOT_URLCONF = 'tests.urls'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'dynamic_preferences',
    'tests.test_app'
]
SITE_ID = 1
SECRET_KEY = 'FDLDSKSDJHF'
STATIC_URL = '/static/'
NOSE_ARGS = ['-s']
MIDDLEWARE_CLASSES =  (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


def check_django_version(minimal_version):
    import django
    from distutils.version import LooseVersion
    django_version = django.get_version()
    return LooseVersion(minimal_version) <= LooseVersion(django_version)


if check_django_version("1.8"):
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.request',
                    'dynamic_preferences.processors.global_preferences',
                ],
            },
        },
    ]
else:
    from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
    TEMPLATE_CONTEXT_PROCESSORS = list(TEMPLATE_CONTEXT_PROCESSORS) + [
        'django.core.context_processors.request',
        'dynamic_preferences.processors.global_preferences',
    ]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
CACHE_DYNAMIC_PREFERENCES_SETTINGS = False
