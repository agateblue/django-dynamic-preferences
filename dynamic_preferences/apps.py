from django.apps import AppConfig
from django.conf import settings

from .registries import preference_models, user_preferences_registry, global_preferences_registry


class DynamicPreferencesConfig(AppConfig):
    name = 'dynamic_preferences'
    verbose_name = "Dynamic Preferences"

    def ready(self):
        UserPreferenceModel = self.get_model('UserPreferenceModel')
        GlobalPreferenceModel = self.get_model('GlobalPreferenceModel')

        preference_models.register(UserPreferenceModel, user_preferences_registry)
        preference_models.register(GlobalPreferenceModel, global_preferences_registry)

        # This will load all dynamic_preferences_registry.py files under isntalled apps
        global_preferences_registry.autodiscover(settings.INSTALLED_APPS)
