=======
Upgrade
=======

0.8
***

.. warning::

    there is a backward incompatbile change in this release.

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
