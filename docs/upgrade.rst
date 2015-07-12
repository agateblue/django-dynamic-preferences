=======
Upgrade
=======

0.5
***

The 0.5 release implies a migration from ``TextField`` to ``CharField`` for ``name`` and ``section`` fields.

This migration is handled by the package for global and per-user preferences. However, if you created your
own preference model, you'll have to generate the migration yourself.

You can do it via ``python manage.py makemigrations <your_app>``

After that, just run a ``python manage.py syncdb`` and you'll be done. 
