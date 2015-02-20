Custom per-instance preferences
========================

By default, dynamic-preferences come with two kinds of preferences:

- Global preferences, which are not tied to any particular model instance
- User preferences, which apply to a specific user

While this can be enough, your project may require additional preferences. For example, you may want to bind preferences to a specific ``Site`` instance. Don't panic, dynamic-preferences got you covered.

In order to achieve this, you'll need to follow this process:

1. Create a registry to store available preferences for sites
2. Create a preference model with a ForeignKey to Site

Lets'go::

.. code-block: python

    # yourapp/models.py
    from django.contrib.sites.models import Site

    from dynamic_preferences.registries import PerInstancePreferencesRegistry
    from dynamic_preferences.models import PerInstancePreferenceModel

    # here, we create our registry
    site_preferences = PerInstancePreferencesRegistry()


    class SitePreferenceModel(PerInstancePreferenceModel):
        """A model to store per-site preferences"""

        # You don't have to set a related name, but it'll probably be convenient
        instance = models.ForeignKey(Site, related_name="preferences")
        registry = site_preferences


Now, you can create a migration for your newly created model with ``python manage.py makemigrations``, apply it with ``python manage.py syncdb`` and start registering your first preferences::

.. code-block:: python
    
    from yourapp.models import site