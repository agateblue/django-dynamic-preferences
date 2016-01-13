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
    )


Glossary
********

.. glossary::

    Preference
        An object that deals with preference logic, such as serialization, deserialization, form display, default values, etc.
        After being defined, preferences can be tied via registries to one ore many preference models, which will deal with database persistence.

    PreferenceModel
        A model that store preferences values in database. A preference model may be tied to a particular instance, which is the case for UserPreferenceModel, or concern the whole project, as GlobalPreferenceModel.

Create and register your own preferences
****************************************

In this example, we assume you are building a blog. Some preferences will apply to your whole project, while others will belong to specific users.

First, create a `dynamic_preferences_registry.py` file within one of your project app. The app must be listed in :py:const:`settings.INSTALLED_APPS`.

Let's declare a few preferences in this file:

.. code-block:: python

    # blog/dynamic_preferences_registry.py

    from dynamic_preferences.types import BooleanPreference, StringPreference, Section
    from dynamic_preferences import user_preferences_registry, global_preferences_registry

    # we create some section objects to link related preferences together

    general = Section('general')
    discussion = Section('discussion')

    # We start with a global preference
    @global_preferences_registry.register
    class SiteTitle(StringPreference):
        section = general
        name = 'title'
        default = 'My site'

    @global_preferences_registry.register
    class MaintenanceMode(BooleanPreference):
        name = 'maintenance_mode'
        default = False

    # now we declare a per-user preference
    @user_preferences_registry.register
    class CommentNotificationsEnabled(BooleanPreference):
        """Do you want to be notified on comment publication ?"""
        section = discussion
        name = 'comment_notifications_enabled'
        default = True


The :py:attr:`section` attribute is a convenient way to keep your preferences in different... well... sections. While you can totally forget this attribute, it is used in various places like admin or forms to filter and separate preferences. You'll probably find it useful if you have many different preferences.
The :py:attr:`name` attribute is a unique identifier for your preference. However, You can share the same name for various preferences if you use different sections.

.. important::
    preferences names and sections names (if you use them) are persisted in database and should be considered as primary keys.
    If, for some reason, you want to update a preference or section name and keep already persisted preferences sync,
    you'll have to write a data migration.

Retrieve and update preferences
*******************************

You can get and update preferences via a ``Manager``, a dictionary-like object. The logic is almost exactly the same for global preferences and per-instance preferences.

.. code-block:: python

    from dynamic_preferences import global_preferences_registry

    # We instantiate a manager for our global preferences
    global_preferences = global_preferences_registry.manager()

    # now, we can use it to retrieve our preferences
    # the lookup for a preference has the following form: <section>__<name>
    assert global_preferences['general__title'] == 'My site'

    # You can also access section-less preferences
    assert global_preferences['maintenance_mode'] == False

    # We can update our preferences values the same way
    global_preferences['maintenance_mode'] = True

For per-instance preferences it's even easier. You can access each instance preferences via the ``preferences`` attribute.

.. code-block:: python

    from django.contrib.auth import get_user_model

    user = get_user_model().objects.get(username='eliot')

    assert user.preferences['discussion__comment_notifications_enabled'] == True

    # Disable the notification system
    user.preferences['discussion__comment_notifications_enabled'] = False

Under the hood
--------------

When you access a preference value (e.g. via ``global_preferences['maintenance_mode']``), dynamic-preferences follows these steps:

1. It checks for the cached value (using classic django cache mechanisms)
2. If no cache key is found, it queries the database for the value
3. If the value does not exists in database, a new row is added with the default preference value, and the value is returned. The cache is updated to avoid another database query the nex time you want to retrieve the value.

Therefore, in the worst-case scenario, accessing a single preference value can trigger up to two database queries. Most of the time, however, dynamic-preferences will only hit the cache.

When you set a preference value (e.g. via``global_preferences['maintenance_mode'] = True``), dynamic-preferences follows these steps:

1. The corresponding row is queried from the database (1 query)
2. The new value is set and persisted in db (1 query)
3. The cache is updated.

Updating a preference value will always trigger two database queries.

Misc methods for retrieving preferences
---------------------------------------

A few other methods are available on managers to retrieve preferences:

- `manager.all()`: returns a `dict` containing all preferences identifiers and values
- `manager.by_name()`: returns a `dict` containing all preferences identifiers and values.
   The preference section name (if any) is removed from the identifier
- `manager.get_by_name(name)`: returns a single preference value using only the preference name

About serialization
*******************

When you get or set preferences values, you interact with Python values. On the database/cache side, values are serialized before storage.

Dynamic preferences handle this for you, using each preference type (BooleanPreference, StringPreference, IntPreference, etc.). It's totally possible to create your own preferences types and serializers, have a look at ``types.py`` and ``serializers.py`` to get started.


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
    # You can use the lookup notation (section__name) as follow
    form_class = global_preference_form_builder(preferences=['general__title'])

    # or pass explicitly the section and names as an iterable of tuples
    form_class = global_preference_form_builder(preferences=[('general', 'title'), ('another_section', 'another_name')])


Getting a form for a specific instance preferences works similarly, except that you need to provide the user instance:

.. code-block:: python

    from dynamic_preferences.forms import user_preference_form_builder

    form_class = user_preference_form_builder(instance=request.user)
    form_class = user_preference_form_builder(instance=request.user, section='discussion')

Preferences attributes
**********************

You can customize a lof of preferences behaviour some class attributes / methods.

For example, if you want to customize the ``verbose_name`` of a preference you can simply do:

.. code-block:: python

    class MyPreference(StringPreference):
        verbose_name = "This is my preference"

But if you need more customization, you can do:

.. code-block:: python

    import datetime

    class MyPreference(StringPreference):

        def get_verbose_name(self):
            return "Verbose name instantiated on {0}".format(datetime.datetime.now())

Both methods are perfectly valid. You can override the following attributes:

* ``field_class``: the field class used to edit the preference value
* ``field_kwargs``: kwargs that are passed to the field class upon instantiation. Ensure to call ``super()`` since some default are provided.
* ``verbose_name``: used in admin and as a label for the field
* ``help_text``: used in admin and in the field
* ``default``: the default value for the preference, taht will also be used as initial data for the form field
* ``widget``: the widget used for the form field

Accessing global preferences within a template
**********************************************

Dynamic-preferences provide a context processors (remember to add them to your settings, as described in "Installation") that will pass global preferences values to your templates:

.. code-block:: html+django

    # myapp/templates/mytemplate.html

    <title>{{ global_preferences.general__title }}</title>

    {% if request.user.preferences.discussion__comment_notifications_enabled %}
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
