.. django-dynamic-preferences documentation master file, created by
   sphinx-quickstart on Sat Jun 28 13:23:43 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Django-dynamic-preferences documentation
========================================

Dynamic-preferences is a Django app, BSD-licensed, designed to manage your project settings. While most of the time,
a `settings.py` file is sufficient, there are some situations where you need something more flexible,
such as per-user settings and per-site settings.

For per-user settings, you could actually store them in `UserProfile`. However, it means that every time you want to add a new setting, you need to add a new column to the `UserProfile` DB table. Not very efficient.

Dynamic-preferences allow you to register settings (a.k.a. preferences) in a declarative way, for users or your whole project. Preferences values are serialized before storage in database, and automatically deserialized when you want to access them. It's also possible to create your own preference classes, binded to the model of your choice, such as per-site preferences.

With dynamic-preferences, you can update settings on the fly, through django's admin or custom forms, without restarting your application.

The project is tested and work under Python 2.7 and 3.4, with django 1.7. Previous django versions are not supported.

If you're still interessed, head over :doc:`quickstart`.

Contents:

.. toctree::
   :maxdepth: 2

   quickstart
   settings
   contributing
   authors
   history
   readme
