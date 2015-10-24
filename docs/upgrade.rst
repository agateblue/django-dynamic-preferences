=======
Upgrade
=======

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
