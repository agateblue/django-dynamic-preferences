=============================
django-dynamic-preferences
=============================

.. image:: https://badge.fury.io/py/django-dynamic-preferences.png
    :target: https://badge.fury.io/py/django-dynamic-preferences

.. image:: https://readthedocs.org/projects/django-dynamic-preferences/badge/?version=latest
    :target: http://django-dynamic-preferences.readthedocs.org/en/latest/

.. image:: https://travis-ci.org/EliotBerriot/django-dynamic-preferences.svg?branch=master
    :target: https://travis-ci.org/EliotBerriot/django-dynamic-preferences

.. image:: https://travis-ci.org/EliotBerriot/django-dynamic-preferences.svg?branch=develop
    :target: https://travis-ci.org/EliotBerriot/django-dynamic-preferences

Dynamic-preferences is a Django app, BSD-licensed, designed to help you manage your project settings. While most of the time,
a `settings.py` file is sufficient, there are some situations where you need something more flexible such as:

* per-user settings (or, generally speaking, per instance settings)
* settings change without server restart

For per-instance settings, you could actually store them in some kind of profile model. However, it means that every time you want to add a new setting, you need to add a new column to the profile DB table. Not very efficient.

Dynamic-preferences allow you to register settings (a.k.a. preferences) in a declarative way. Preferences values are serialized before storage in database, and automatically deserialized when you need them.

With dynamic-preferences, you can update settings on the fly, through django's admin or custom forms, without restarting your application.

The project is tested and work under Python 2.7 and 3.4, with django >=1.7.

Features
--------

* Simple to setup
* Admin integration
* Forms integration
* Bundled with global and per-user preferences
* Can be extended to other models if need (e.g. per-site preferences)
* Integrates with django caching mechanisms to improve performance

Documentation
-------------

The full documentation is at https://django-dynamic-preferences.readthedocs.org.

Contributing
------------

See http://django-dynamic-preferences.readthedocs.org/en/latest/contributing.html
