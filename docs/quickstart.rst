Quickstart
==========

Installation
************

Dynamic-preferences is available on `PyPi <https://pypi.python.org/pypi/django-dynamic-preferences>`_ and can be installed with::

    pip install django-dynamic-preferences

Setup
*****

Add this to your :py:const:`settings.INSTALLED_APPS`::

    INSTALLED_APPS = (
        # ...
        'django.contrib.sites',
        'django.contrib.auth',
        'dynamic_preferences',        
    )

Activate autodiscovering of registered preferences by appending the following to your `urls.py`::

    from dynamic_preferences.registries import autodiscover
    autodiscover()

By calling :py:func:`autodiscover`, dynamic-preferences will iterate through each app registered in
:py:const:`settings.INSTALLED_APPS`, trying to import :py:mod:`dynamic_preferences_registry` package.

Register preferences
********************

First, create a `dynamic_preferences_registry.py` file within one of your project app. The app must be listed in :py:const:`settings.INSTALLED_APPS`. You can of course have a `dynamic_preferences_registry.py` file in multiple apps.

Let's declare a few preferences in this file::

    from dynamic_preferences.preferences import UserPreference, GlobalPreference
    from dynamic_preferences.types import BooleanPreference, StringPreference
    from dynamic_preferences.registries import register

    @register
    class RegistrationAllowed(BooleanPreference, GlobalPreference):
        """
        Are new registrations allowed ?
        """
        section = "auth"
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

Note how we build our preferences object by inheriting from two base classes. :py:mod:`dynamic_preferences.preferences` classes such as :py:class:`GlobalPreference` and :py:class:`UserPreference` describe the level of your preference, i.e. if it apply to a user, a site, or globally. :py:mod:`dynamic_preferences.types` classes describe the data type you want to store in your preference (an integer, a boolean, a string...).

The :py:attr:`section` attribute is a convenient way to keep your preferences in different... well... sections. While you can totally forget this attribute, it is used in various places like admin or forms to filter and separate preferences. You'll probably find it useful if you have many different preferences.

The :py:attr:`name` attribute is a unique identifier for your preference. However, You can share the same name for various preferences if you use different sections.

Retrieve and update preferences
*******************************

Most of the time, you probably won't need to manipulate preferences by hand, and prefer to rely on forms and admin interface. Just in case, here is a quick overview of how you can interact with preferences::

    from dynamic_preferences.models import global_preferences, user_preferences

    # let's start with our global preference
    # Retrieve the model object corresponding to our preference
    # we use django's regular get_or_create method to create the preference if it does not exist

    registration_allowed_preference, created = global_preferences.get_or_create(section="auth",
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
    favorite_colour_preference, created = user_preferences.get_or_create(section="misc", name="favorite_colour",
    user=henri)

    assert favorite_colour_preference.value == 'Green'

    # Update the value

    favorite_colour_preference.value = 'Blue'
    favorite_colour_preference.save()

    # Note that you can also access preferences directly from a User instance

    assert henri.preferences.get(section="misc", name="favorite_colour").value == 'Blue'

:py:obj:`global_preferences` and :py:obj:`user_preferences` are regular `Django managers <https://docs.djangoproject.com/en/dev/topics/db/managers/>`_, and they return standard models, so there is nothing new here.

Admin integration
*****************

Dynamic-preferences integrates with `django.contrib.admin` out of the box. You can therefore use the admin interface to edit preferences values, which is particularly convenient for global and per-site preferences.

Accessing preferences values within a template
**********************************************

Dynamic-preferences provide some context processors (remember to ad them to your settings, as described in "Installation") that will pass registries values to your templates context. You can access passed values as follows::

    # in myapp/mytemplate.html

    {% if global_preferences.auth.registration_allowed %}
        You can register an account on the website
    {% else %}
        Registrations are closed now
    {% endif %}

    # accessing user preferences requires an authenticated user

    {% if request.user.is_authenticated %}
        Hello {{ request.user.username }}, your favorite colour is {{ user_preferences.misc.favorite_colour }}.
    {% endif %}

Display preferences forms
*************************

When you want your preferences to be editable by users who do not have access to admin interface (which should be the case for user preferences), you can use bundled URLs and views. All you need is to include dynamic-preferences' urls into your application::

    urlpatterns = patterns('',    
        # ...
        url(r'^preferences/', include('dynamic_preferences.urls')),
    )

Then, in your code::

    from django.core.urlresolvers import reverse

    # URL to a page that display a form to edit all global preferences
    url = reverse("dynamic_preferences.global")

    # URL to a page that display a form to edit global preferences listed in section 'auth'
    url = reverse("dynamic_preferences.global.section", kwargs={'section': 'auth'})

    # URL to a page that display a form to edit all preferences of the user making the request
    url = reverse("dynamic_preferences.user")

    # URL to a page that display a form to edit preferences listed under section 'misc' of the user making the request
    url = reverse("dynamic_preferences.user.section", kwargs={'section': 'misc'})

Keep registries in sync with you database
*****************************************

If you add or remove preferences from your `dynamic_preferences_registry.py`, you may encounter `KeyError` exceptions when you try to display preferences related forms or admin pages. This happens because you have preferences instances in your database that does not correspond to any registered preference object in your registries. 

To solve this, you can run ``python manage.py checkpreferences`` inside your project. This command will check every preference in database, and remove/create needed ones. Please note this can take some time if you have many users.

A few settings
**************

Dynamic-preferences has a few settings you can modify in your `settings.py`.

- :py:const:`CREATE_DEFAULT_PREFERENCES_FOR_NEW_USERS` : will create default preferences objects in database each time a new user is added (default is True). At the moment, this setting will only work with :py:class:`django.contrib.auth.models.User`.



