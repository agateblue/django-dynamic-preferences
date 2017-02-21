from django.apps import AppConfig, apps
from django.conf import settings

from ..registries import preference_models
from .registries import user_preferences_registry


class UserPreferencesConfig(AppConfig):
    name = 'dynamic_preferences.users'
    verbose_name = "Preferences - Users"
    label = 'dynamic_preferences_users'

    def ready(self):
        UserPreferenceModel = self.get_model('UserPreferenceModel')

        preference_models.register(
            UserPreferenceModel, user_preferences_registry)
