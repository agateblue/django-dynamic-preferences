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
    )

Then, create missing tables in your database::

    python manage.py migrate dynamic_preferences

Add this to :py:const:`settings.TEMPLATE_CONTEXT_PROCESSORS` if you want to access preferences from templates::

    TEMPLATE_CONTEXT_PROCESSORS =  (
        'django.core.context_processors.request',
        'dynamic_preferences.processors.global_preferences',
    )
