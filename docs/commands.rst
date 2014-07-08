Commands
========

Dynamic-preferences is bundles with a few commands that help you preserve your database integrity. These are regular
django commands you can invoke with ``python manage.py <commandname>``.

Checkpreferences
****************

This command will check that every preference in database correspond to a registered preference. It's particularly
useful when you remove a preference for your ``dynamic_preferences_registry.py`` file,
because corresponding model instances are not automatically deleted from your database,
a situation that will lead to errors accross your project.

``checkpreferences`` handle this for you and will delete preferences model when no corresponding preference is found
in registries.
