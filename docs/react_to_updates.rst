React to updates of preferences
===============================

Sometimes, it may be necessary to do something once a preference was
updated, e.g. invalidate some caches, re-generate a stylesheet, or
whatever.

Therefore, a signal is emitted after any preference was updated.


Writing a signal receiver
-------------------------

First, you need to write a signal receiver that runs code once the signal is
emitted. A signal receiver is a simple function that takes the arguments
of the signal, which are:

* ``sender`` - the ``PreferenceManager`` of the changed preference
* ``section`` - the section in which a preference was changed
* ``name`` - the name of the changed preference
* ``old_value`` - the value of the preference before changing
* ``new_value`` - the value assigned to the preference after the change

An example that just prints a message that the preference was changed is
below.

.. code-block:: python

    # yourapp/util.py

    def notify_on_preference_update(sender, section, name, old_value, new_value, **kwargs):
        print("Preference {} in section {} changed from {} to {}".format(
            name, section, old, new))


Registering the receiver
------------------------

You must register the signal receiver at some point, e.g. in the ``ready``
method of your app.

.. code-block:: python

    # yourapp/apps.py
    from django.apps import AppConfig

    from dynamic_preferences.signals import preference_updated

    from .util import notify_on_preference_update


    class YourAppConfig(AppConfig):
        def ready(self):
            preference_updated.connect(notify_on_preference_update)
