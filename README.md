**Warning: This project should not be considered as stable at the moment.**

# What is dynamic-preferences ?

Dynamic-preferences is a Django app designed to manage your project settings. While most of the time,
a `settings.py` file is sufficient, there are some situations where you need something more flexible,
such as per-user settings and per-site settings.

For per-user settings, you could actually store them in `UserProfile`. However, it means that every time you want to add a new setting, you need to add a new column to the `UserProfile` DB table. Not very efficient.

Dynamic-preferences allow you to register settings (a.k.a. preferences) in a declarative way, for users,
sites and your whole project. Preferences values are serialized before storage in database,
and automatically deserialized when you want to access them.

With dynamic-preferences, you can update settings on the fly, through django's admin or custom forms, without restarting your application.

Links:

- [Project page](http://code.eliotberriot.com/eliotberriot/django-dynamic-preferences)
- [Documentation](http://django-dynamic-preferences.readthedocs.org)
- [PyPi package](https://pypi.python.org/pypi/django-dynamic-preferences)


# Changelog

## 0.3

This version breaks compatibility with 0.2.on 

- Dropped support of django < 1.7
- Tests refactoring
- Added database migrations
- Deleted SitePreferenceModel in favor of a more generic solution (PerInstancePreferenceModel). UserPreferenceModel is still here because it will be commonly used.
- Major API cleanup

# License

The project is licensed under BSD licence.