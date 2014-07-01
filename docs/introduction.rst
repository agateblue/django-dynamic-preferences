What is dynamic-preferences ?
=============================

Dynamic-preferences is a Django app designed to manage your project settings. While most of the time,
a `settings.py` file is sufficient, there are some situations where you need something more flexible,
such as per-user settings and per-site settings.

For per-user settings, you could actually store them in `UserProfile`. However, it means that every time you want to
add a new setting, you need to add a new column to the `UserProfile` DB table. Not very efficient.

Dynamic-preferences allow you to register settings (a.k.a. preferences) in a declarative way, for users,
sites and your whole project. Preferences values are serialized before storage in database,
and automatically deserialized when you want to access them.

Quickstart
==========

Register preferences
********************

First, create a `dynamic_preferences_registry.py` file within one of your project app. The app must be listed in
:py:const:`settings.INSTALLED_APPS`.

Let's declare a few preferences in this file::

    from dynamic_preferences.models import UserPreference, GlobalPreference
    from dynamic_preferences.types import BooleanPreference, StringPreference
    from dynamic_preferences.registries import register

    @register
    class RegistrationAllowed(BooleanPreference, GlobalPreference):
        """
        Are new registrations allowed ?
        """
        section = "user"
        name = "registration_allowed"
        default = False


    @register
    class FavoriteColour(StringPreference, UserPreference):
        """
        What's your favorite colour ?
        """
        section = "misc"
        name = "favorite_colour"
        default = "Green"

Now, we need to activate autodiscovering of registered preferences. Add the following at the end of your URLconf::

    from dynamic_preferences.registries import autodiscover
    autodiscover()

By calling :py:func:`autodiscover`, dynamic-preferences will iterate through each app registered in
:py:const:`settings.INSTALLED_APPS`, trying to import :py:mod:`dynamic_preferences_registry` package.

Retrieve and update preferences
*******************************

Now, we'll probably want to interact with our preferences::

    from dynamic_preferences.models import global_preferences, user_preferences

    # let's start with our global preference

    # Retrieve the model object corresponding to our preference
    # 
    registration_allowed_preference, created = global_preferences.get_or_create(section="user",
    name="registration_allowed")

    # get the value (Should be False, since RegistrationAllowed.default is False)
    registration_is_allowed = registration_allowed_preference.value
    assert registration_is_allowed == False

    # preferences are regular models, and can be updated the same way
    registration_allowed_preference.value = True
    registration_allowed_preference.save()

    # dealing with user preferences is quite similar, except you need to provide the corresponding User instance
    from django.contrib.auth.models import User

    henri = User.objects.get(username="henri")
    favorite_colour_preference = user_preferences.get(section="misc", name="favorite_colour", user=henri)

    assert favorite_colour_preference.value == 'Green'

    # Update the value
    favorite_colour_preference.value = 'Blue'
    favorite_colour_preference.save()

    # Note that you can also access preferences directly from a User instance

    assert henri.preferences.get(section="misc", name="favorite_colour").value == 'Blue'