=======
Upgrade
=======

1.0
****

In order to fix #33 and to make the whole package lighter and more modular for the 1.0 release,
user preferences where moved to a dedicated app.

If you were using user preferences before and want to use them after the package, upgrade will require a few changes
to your existing code, as described below.

If you only use the package for the global preferences, no change should be required on your side, apart from running the migrations.

Add the app to your INSTALLED_APPS
----------------------------------

In ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'dynamic_preferences',
        'dynamic_preferences.users.apps.UserPreferencesConfig',  # <---- add this line
    ]

Replace old imports
-------------------

Some functions and classes were moved to the dedicated ``dynamic_preferences.users`` app.

The following imports will crash:

.. code-block:: python

    from dynamic_preferences.registry import user_preferences_registry
    from dynamic_preferences.forms import (
        UserSinglePreferenceForm,
        user_preference_form_builder,
        UserPreferenceForm,
    )
    from dynamic_preferences.views import UserPreferenceFormView
    from dynamic_preferences.models import UserPreferenceModel

You should use the following imports instead:

.. code-block:: python

    from dynamic_preferences.users.registry import user_preferences_registry
    from dynamic_preferences.users.forms import (
        UserSinglePreferenceForm,
        user_preference_form_builder,
        UserPreferenceForm,
    )
    from dynamic_preferences.users.views import UserPreferenceFormView
    from dynamic_preferences.users.models import UserPreferenceModel

.. note::

    It is mandatory to update the path for ``user_preferences_registry``. Other paths are part of the public API but their use is optional and varies depending of how you usage of the package.

Run the migrations
-------------------------

User preferences were stored on the ``UserPreferenceModel`` model class.

The migrations only rename the old table to match the fact that the model was moved in another app. Otherwise, nothing should be deleted or altered at all, and you can inspect the two related migrations to see what we're doing:

- dynamic_preferences.0004_move_user_model
- dynamic_preferences.users.0001_initial

Anyway, please perform a backup before any database migration.

Once you're ready, just run::

    python manage.py migrate dynamic_preferences_users

.. note::

    If your own code was using ForeignKey fields pointing to ``UserPreferenceModel``, it is likely your code will break with this migration, because your foreign keys will point to the old database table.

    Such foreign keys were not officially supported or recommended though, and should not be needed in the uses cases dynamic_preferences was designed for. However, if you're in this situation, please file an issue on the issue tracker to see what we can do.

Remove useless setting
------------------------

In previous versions, to partially address #33, a ``ENABLE_USER_PREFERENCES`` setting was added to enable / disable the admin endpoints for user preferences. Since you can now opt into user preferences via ``INSTALLED_APPS``, this setting is now obsolete and can be safely removed from your settings file.


0.8
***

.. warning::

    there is a backward incompatible change in this release.

To address #45 and #46, an import statement was removed from __init__.py.
Because of that, every file containing the following:

.. code-block:: python

    from dynamic_preferences import user_preferences_registry, global_preferences_registry

Will raise an `ImportError`.

To fix this, you need to replace by this:

.. code-block:: python

    #                       .registries was added
    from dynamic_preferences.registries import user_preferences_registry, global_preferences_registry

0.6
***

Sections are now plain python objects (see #19). When you use sections in your code,
instead of the old notation:

.. code-block:: python

    from dynamic_preferences.types import BooleanPreference

    class MyPref(BooleanPreference):
        section = 'misc'
        name = 'my_pref'
        default = False

You should do:

.. code-block:: python

    from dynamic_preferences.types import BooleanPreference, Section

    misc = Section('misc')

    class MyPref(BooleanPreference):
        section = misc
        name = 'my_pref'
        default = False

Note that the old notation is only deprecated and will continue to work for some time.

0.5
***

The 0.5 release implies a migration from ``TextField`` to ``CharField`` for ``name`` and ``section`` fields.

This migration is handled by the package for global and per-user preferences. However, if you created your
own preference model, you'll have to generate the migration yourself.

You can do it via ``python manage.py makemigrations <your_app>``

After that, just run a ``python manage.py syncdb`` and you'll be done.
