from django.apps import AppConfig

from . import global_preferences_registry
from .registries import autodiscover


class DynamicPreferencesConfig(AppConfig):
    name = 'dynamic_preferences'
    verbose_name = "Dynamic Preferences"

    def ready(self):
        autodiscover()

        
