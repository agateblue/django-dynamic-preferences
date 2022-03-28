============
Installation
============

Dynamic-preferences is available on `PyPI <https://pypi.python.org/pypi/django-dynamic-preferences>`_ and can be installed with::

    pip install django-dynamic-preferences

Setup
*****

Add this to your :py:const:`settings.INSTALLED_APPS`::

    INSTALLED_APPS = (
        # ...
        'django.contrib.auth',
        'dynamic_preferences',
        # comment the following line if you don't want to use user preferences
        'dynamic_preferences.users.apps.UserPreferencesConfig',
    )

Then, create missing tables in your database::

    python manage.py migrate dynamic_preferences

Add this to :py:const:`settings.TEMPLATES` if you want to access preferences from templates::

    TEMPLATES = [
        {
            # ...
            'OPTIONS': {
                'context_processors': [
                    # ...
                    'django.template.context_processors.request',
                    'dynamic_preferences.processors.global_preferences',
                ],
            },
        },
    ]

Settings
********

Also, take some time to look at provided settings if you want to customize the package behaviour:

.. code-block:: python

        # available settings with their default values
        DYNAMIC_PREFERENCES = {

            # a python attribute that will be added to model instances with preferences
            # override this if the default collide with one of your models attributes/fields
            'MANAGER_ATTRIBUTE': 'preferences',

            # The python module in which registered preferences will be searched within each app
            'REGISTRY_MODULE': 'dynamic_preferences_registry',

            # Allow quick editing of preferences directly in admin list view
            # WARNING: enabling this feature can cause data corruption if multiple users
            # use the same list view at the same time, see https://code.djangoproject.com/ticket/11313
            'ADMIN_ENABLE_CHANGELIST_FORM': False,

            # Customize how you can access preferences from managers. The default is to
            # separate sections and keys with two underscores. This is probably not a settings you'll
            # want to change, but it's here just in case
            'SECTION_KEY_SEPARATOR': '__',

            # Use this to disable auto registration of the GlobalPreferenceModel.
            # This can be useful to register your own model in the global_preferences_registry.
            'ENABLE_GLOBAL_MODEL_AUTO_REGISTRATION': True,

            # Use this to disable caching of preference. This can be useful to debug things
            'ENABLE_CACHE': True,

            # Use this to select which chache should be used to cache preferences. Defaults to default.
            'CACHE_NAME': 'default',

            # Use this to disable checking preferences names. This can be useful to debug things
            'VALIDATE_NAMES': True,
        }
