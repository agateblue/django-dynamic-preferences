from django.apps import AppConfig

from . import global_preferences_registry
from .registries import autodiscover, preference_models
from .dynamic_preferences_registry import user_preferences_registry, global_preferences_registry


class DynamicPreferencesConfig(AppConfig):
    name = 'dynamic_preferences'
    verbose_name = "Dynamic Preferences"

    def ready(self):
        UserPreferenceModel = self.get_model('UserPreferenceModel')
        GlobalPreferenceModel = self.get_model('GlobalPreferenceModel')

        preference_models.register(UserPreferenceModel, user_preferences_registry)
        preference_models.register(GlobalPreferenceModel, global_preferences_registry)

        autodiscover()
