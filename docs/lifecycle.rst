Preferences lifecycle
======================


Update
******

To do, help welcome :)

Deletion
********

If you remove preferences from your registry, corresponding data rows won't be deleted automatically.

In order to keep a clean database and delete obsolete rows, you can use the `checkpreferences` management command. This command will check all preferences in database, ensure they match a registered preference class and delete rows that do not match any registered preference.

.. warning::

    Run this command carefully, since it can lead to data loss.
