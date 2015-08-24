Settings
========

Some settings are available if you want to adapt dynamic-preferences to your needs

.. code:: python

        # available settings with their default values
        DYNAMIC_PREFERENCES = {

            # a python attribute that will be added to model instances with preferences
            # override this if the default collide with one of your models attributes/fields
            'MANAGER_ATTRIBUTE': 'preferences',

            # The python module in which registered preferences will be searched within each app
            'REGISTRY_MODULE': 'dynamic_preferences_registry',

            # Allow quick editing of preferences directly in admin list view
            # WARNING: enabling this feature can cause data corruption if multiple users
            use the same list view at the same time, see https://code.djangoproject.com/ticket/11313
            'ADMIN_ENABLE_CHANGELIST_FORM': False,
        }
