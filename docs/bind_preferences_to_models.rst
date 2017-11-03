Bind preferences to arbitrary models
====================================

By default, dynamic-preferences come with two kinds of preferences:

- Global preferences, which are not tied to any particular model instance
- User preferences, which apply to a specific user

While this can be enough, your project may require additional preferences. For example, you may want to bind preferences to a specific ``Site`` instance. Don't panic, dynamic-preferences got you covered.

In order to achieve this, you'll need to follow this process:

1. Create a preference model with a ForeignKey to Site
2. Create a registry to store available preferences for sites

The following guide assumes you want to bind preferences to the ``django.contrib.sites.Site`` model.


Create a preference model
-------------------------

You'll need to subclass ``PerInstancePreferenceModel`` model,
and add a ``ForeignKey`` field pointing to the target model:

.. code-block:: python

    # yourapp/models.py
    from django.contrib.sites.models import Site
    from dynamic_preferences.models import PerInstancePreferenceModel

    class SitePreferenceModel(PerInstancePreferenceModel):

        # note: you *have* to use the `instance` field
        instance = models.ForeignKey(Site)

        class Meta:
            # Specifying the app_label here is mandatory for backward
            # compatibility reasons, see #96
            app_label = 'yourapp'

Now, you can create a migration for your newly created model with ``python manage.py makemigrations``, apply it with ``python manage.py migrate``.

Create a registry to collect your model preferences
---------------------------------------------------

Now, you have to create a registry to collect preferences belonging to the ``Site`` model:

.. code-block:: python

    # yourapp/registries.py
    from dynamic_preferences.registries import PerInstancePreferenceRegistry

    class SitePreferenceRegistry(PerInstancePreferenceRegistry):
        pass

    site_preferences_registry = SitePreferenceRegistry()

Then, you simply have to connect your ``SitePreferenceModel`` to your registry. You should do that in
an ``apps.py`` file, as follows:

.. code-block:: python

    # yourapp/apps.py
    from django.apps import AppConfig
    from django.conf import settings

    from dynamic_preferences.registries import preference_models
    from .registries import site_preferences_registry

    class YourAppConfig(AppConfig):
        name = 'your_app'

        def ready(self):
            SitePreferenceModel = self.get_model('SitePreferenceModel')

            preference_models.register(SitePreferenceModel, site_preferences_registry)

Here, we use django's built-in ``AppConfig``, which is a convenient place to put this kind of logic.

To ensure this config is actually used by django, you'll also have to edit your app ``__init__.py``:

.. code-block:: python

    # yourapp/__init__.py
    default_app_config = 'yourapp.apps.YourAppConfig'

.. warning::

    Ensure your app is listed **before** ``dynamic_preferences`` in ``settings.INSTALLED_APPS``,
    otherwise, preferences will be collected before your registry is actually registered, and it will end up empty.

Start creating preferences
--------------------------

After this setup, you're good to go, and can start registering your preferences for the ``Site`` model in the same way
you would do with the ``User`` model. You'll simply need to use your registry instead of the ``user_preferences_registry``:

.. code-block:: python

    # yourapp/dynamic_preferences_registry.py
    from dynamic_preferences.types import BooleanPreference, StringPreference
    from dynamic_preferences.preferences import Section
    from yourapp.registries import site_preferences_registry

    access = Section('access')

    @site_preferences_registry.register
    class IsPublic(BooleanPreference):
        section = access
        name = 'is_public'
        default = False

Preferences will be available on your ``Site`` instances using the ``preferences`` attribute, as described in :doc:`quickstart </quickstart>`:

.. code-block:: python

    # somewhere in a view
    from django.contrib.sites.models import Site

    my_site = Site.objects.first()
    if my_site.preferences['access__is_public']:
        print('This site is public')
