.. django-dynamic-preferences documentation master file, created by
   sphinx-quickstart on Sat Jun 28 13:23:43 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Django-dynamic-preferences documentation
========================================

Dynamic-preferences is a Django app, BSD-licensed, designed to help you manage your project settings. While most of the time,
a `settings.py` file is sufficient, there are some situations where you need something more flexible such as:

 * per-user settings (or, generally speaking, per instance settings)
 * settings change without server restart

For per-instance settings, you could actually store them in some kind of profile model. However, it means that every time you want to add a new setting, you need to add a new column to the profile DB table. Not very efficient.

Dynamic-preferences allow you to register settings (a.k.a. preferences) in a declarative way. Preferences values are serialized before storage in database, and automatically deserialized when you need them.

With dynamic-preferences, you can update settings on the fly, through django's admin or custom forms, without restarting your application.

The project is tested and work under Python 2.7 and 3.4, 3.5 and 3.6, with django >=1.8.

Features
--------

* Simple to setup
* Admin integration
* Forms integration
* Bundled with global and per-user preferences
* Can be extended to other models if need (e.g. per-site preferences)
* Integrates with django caching mechanisms to improve performance
* Django REST Framework integration

If you're still interested, head over :doc:`installation`.

.. warning::
    There is a critical bug in version 1.2 that can result in dataloss. Please upgrade to 1.3 as
    soon as possible and do not use 1.2 in production. See `#81 <https://github.com/agateblue/django-dynamic-preferences/pull/81>`_ for more details.

Contents:

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   bind_preferences_to_models
   react_to_updates
   preference_types
   rest_api
   lifecycle
   upgrade
   contributing
   authors
   history
