from django.db import models
from dynamic_preferences.registries import global_preferences_registry


class MyModel(models.Model):
    # We can't use the global preferences until after this
    title = models.CharField(max_length=50)

    def do_something(self):
        # We instantiate a manager for our global preferences
        global_preferences = global_preferences_registry.manager()

        # We can then use our global preferences however we like
        global_preferences["general__presentation"]
