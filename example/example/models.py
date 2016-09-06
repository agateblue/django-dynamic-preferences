from django.db import models
from dynamic_preferences.registries import global_preferences_registry


class myModel(models.Model):
    # We can't use the global preferences until after this
    title = models.CharField()

    def doSomething(self):
        # We instantiate a manager for our global preferences
        global_preferences = global_preferences_registry.manager()

        # We can then use our global preferences however we like
        global_preferences['general__presentation']
