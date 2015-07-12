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
        }
