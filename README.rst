=============================
django-dynamic-preferences
=============================

.. image:: https://badge.fury.io/py/django-dynamic-preferences.png
    :target: https://badge.fury.io/py/django-dynamic-preferences

.. image:: https://readthedocs.org/projects/django-dynamic-preferences/badge/?version=latest
    :target: http://django-dynamic-preferences.readthedocs.org/en/latest/

.. image:: https://github.com/agateblue/django-dynamic-preferences/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/agateblue/django-dynamic-preferences/actions/workflows/tests.yml

.. image:: https://opencollective.com/django-dynamic-preferences/backers/badge.svg
    :alt: Backers on Open Collective
    :target: #backers

.. image:: https://opencollective.com/django-dynamic-preferences/sponsors/badge.svg
    :alt: Sponsors on Open Collective
    :target: #sponsors

.. warning::

    There is a critical bug in version 1.2 that can result in dataloss. Please upgrade to 1.3 as
    soon as possible and do not use 1.2 in production. See `#81 <https://github.com/agateblue/django-dynamic-preferences/pull/81>`_ for more details.

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

Documentation
-------------

The full documentation is at https://django-dynamic-preferences.readthedocs.org.

Changelog
---------

See https://django-dynamic-preferences.readthedocs.io/en/latest/history.html

Contributing
------------

See https://django-dynamic-preferences.readthedocs.org/en/latest/contributing.html

Credits

+++++++

Contributors

------------

This project exists thanks to all the people who contribute!

.. image:: https://opencollective.com/django-dynamic-preferences/contributors.svg?width=890&button=false

Backers

-------

Thank you to all our backers! `Become a backer`__.

.. image:: https://opencollective.com/django-dynamic-preferences/backers.svg?width=890
    :target: https://opencollective.com/django-dynamic-preferences#backers

__ Backer_
.. _Backer: https://opencollective.com/django-dynamic-preferences#backer

Sponsors

--------

Support us by becoming a sponsor. Your logo will show up here with a link to your website. `Become a sponsor`__.

.. image:: https://opencollective.com/django-dynamic-preferences/sponsor/0/avatar.svg
    :target: https://opencollective.com/django-dynamic-preferences/sponsor/0/website

__ Sponsor_
.. _Sponsor: https://opencollective.com/django-dynamic-preferences#sponsor
