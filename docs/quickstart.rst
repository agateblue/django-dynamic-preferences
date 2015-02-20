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
        'django.contrib.auth',
        'dynamic_preferences',        
    )

Then, create missing tables in your database::
    
    python manage.py syncdb


Add this to :py:const:`settings.TEMPLATE_CONTEXT_PROCESSORS` if you want to access preferences from templates::
    
    TEMPLATE_CONTEXT_PROCESSORS =  (
        'django.core.context_processors.request',
        'dynamic_preferences.processors.global_preferences',
        'dynamic_preferences.processors.user_preferences',
    )


Glossary
********

.. glossary::

    Preference
        An object that deals with preference logic, such as serialization, deserialization, form display, default values, etc.
        After being defined, preferences can be tied via registries to one ore many preference models, which will deal with database persistance. 

    PreferenceModel
        A model that store preferences values in database. A preference model may be tied to a particular instance, which is the case for UserPreferenceModel, or concern the whole project, as GlobalPreferenceModel.

    PerInstancePreferenceModel
        Used to store per instance preferences in database. Dynamic preferences is bundled with one kind of per-instance preference model, UserPreferenceModel, but you are free to create your own when needed.

Create and register your own preferences
****************************************

In this example, we assume you are building a blog. Some preferences will apply to your whole project, while others will belong to specific users.

First, create a `dynamic_preferences_registry.py` file within one of your project app. The app must be listed in :py:const:`settings.INSTALLED_APPS`.

Let's declare a few preferences in this file:

.. code-block:: python

    # blog/dynamic_preferences_registry.py

    from dynamic_preferences.types import BooleanPreference, StringPreference
    from dynamic_preferences import user_preferences, global_preferences

    # We start with a global preference
    @global_preferences.register
    class SiteTitle(StringPreference):
        section = 'general'
        name = 'title'
        default = 'My site'

    # now we declare a per-user preference
    @user_preferences.register
    class CommentNotificationsEnabled(BooleanPreference):
        """Do you want to be notified on comment publication ?"""
        section = 'discussion'
        name = 'comment_notifications_enabled'
        default = True


The :py:attr:`section` attribute is a convenient way to keep your preferences in different... well... sections. While you can totally forget this attribute, it is used in various places like admin or forms to filter and separate preferences. You'll probably find it useful if you have many different preferences.

The :py:attr:`name` attribute is a unique identifier for your preference. However, You can share the same name for various preferences if you use different sections.

Retrieve and update preferences
*******************************

Most of the time, you probably won't need to manipulate preferences by hand, and prefer to rely on forms and admin interface. Just in case, here is a quick overview of how you can interact with preferences. Preferences are (almost) regular django models::

    from dynamic_preferences.models import GlobalPreferenceModel, UserPreferenceModel

    # let's start with our global preference
    # Retrieve the model object corresponding to our preference
    # we use django's regular get_or_create method to create the preference if it does not exist
    site_title, created = GlobalPreferenceModel.objects.get_or_create(section='general', name='title')
    assert site_title == 'My site'

    # preferences are regular models, and can be updated the same way
    site_title.value = 'My awesome site'
    site_title.save()

    # dealing with user preferences is quite similar, except you need to provide the corresponding User instance
    from django.contrib.auth.models import User
    henri = User.objects.get(username="henri")
    comment_notifications_enabled, created = user_preferences.get_or_create(section='discussion', name='comment_notifications_enabled', instance=henri)

    assert comment_notifications_enabled.value == True

    # Update the value
    comment_notifications_enabled.value = False
    comment_notifications_enabled.save()

    # Note that you can also access preferences directly from a User instance
    assert henri.preferences.get(section="misc", name="favorite_colour").value == False


About serialization
*******************

Each preference value is serialized into the ``raw_value`` field of a preference model instance before being saved, and deserialized when you access the ``value`` attribute of a preference model intance. Dynamic preferences handle this for you, using your preference type (BooleanPreference, StringPreference, IntPreference, etc.). It's totally possible to create your own preferences types and serializers, have a look at ``types.py`` and ``serializers.py`` to get started.


Admin integration
*****************

Dynamic-preferences integrates with `django.contrib.admin` out of the box. You can therefore use the admin interface to edit preferences values, which is particularly convenient for global preferences.

Forms
*****

A form builder is provided if you want to create and update preferences in custom views.

.. code-block:: python

    from dynamic_preferences.forms import global_preference_form_builder

    # get a form for all global preferences
    form_class = global_preference_form_builder()

    # get a form for global preferences of the 'general' section
    form_class = global_preference_form_builder(section='general')

    # get a form for a specific set of preferences
    # You can use the dotted notation (section.name) as follow
    form_class = global_preference_form_builder(preferences=['general.title'])

    # or pass explicitly the section and names as an iterable of tuples
    form_class = global_preference_form_builder(preferences=[('general', 'title'), ('another_section', 'another_name')])


Getting a form for a specific user preferences works similarly, except that you need to provide the user instance:

.. code-block:: python

    from dynamic_preferences.forms import user_preference_form_builder

    form_class = global_preference_form_builder(instance=request.user)
    form_class = global_preference_form_builder(instance=request.user, section='discussion')
    # etc.    


Accessing preferences values within a template
**********************************************

Dynamic-preferences provide some context processors (remember to add them to your settings, as described in "Installation") that will pass preferences values to your templates context. You can access passed values as follows:

.. code-block:: html+django

    # myapp/templates/mytemplate.html

    <title>{{ global_preferences.general.title }}</title>

    {% if user_preferences.discussion.comment_notifications_enabled %}
        You will receive an email each time a comment is published
    {% else %}
        <a href='/subscribe'>Subscribe to comments notifications</a>
    {% endif %}


Bundled views and urls
**********************

Example views and urls are bundled for global and per-user preferences updating. Include this in your URLconf:

.. code-block:: python

    urlpatterns = [   
        # your project urls here
        url(r'^preferences/', include('dynamic_preferences.urls')),
    ]

Then, in your code::

    from django.core.urlresolvers import reverse

    # URL to a page that display a form to edit all global preferences
    url = reverse("dynamic_preferences.global")

    # URL to a page that display a form to edit global preferences of the general section
    url = reverse("dynamic_preferences.global.section", kwargs={'section': 'general'})

    # URL to a page that display a form to edit all preferences of the user making the request
    url = reverse("dynamic_preferences.user")

    # URL to a page that display a form to edit preferences listed under section 'discussion' of the user making the request
    url = reverse("dynamic_preferences.user.section", kwargs={'section': 'discussion'})


Keep registries in sync with you database
*****************************************

Dynamic preferences does not create default global preferences in database.
In case of per-instance preferences (such as user preferences), each time a model instance with registered preferences is created, it will get default preferences. However, if you declare another preference, already created instances will miss the new preference.

The ``checkpreferences`` command to deal with that. It will:

- Delete useless preferences from your database
- Create missing global and per instance preferences

Run it with ``python manage.py checkpreferences``.
