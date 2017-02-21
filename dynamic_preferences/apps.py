from django.apps import AppConfig, apps
from django.conf import settings

from .registries import preference_models, global_preferences_registry


class DynamicPreferencesConfig(AppConfig):
    name = 'dynamic_preferences'
    verbose_name = "Dynamic Preferences"

    def ready(self):
        GlobalPreferenceModel = self.get_model('GlobalPreferenceModel')

        preference_models.register(
            GlobalPreferenceModel, global_preferences_registry)

        # This will load all dynamic_preferences_registry.py files under
        # installed apps
        app_names = [app.name for app in apps.app_configs.values()]
        global_preferences_registry.autodiscover(app_names)
