from django.apps import AppConfig, apps
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from ..registries import preference_models
from .registries import user_preferences_registry


class UserPreferencesConfig(AppConfig):
    name = "dynamic_preferences.users"
    verbose_name = _("Preferences - Users")
    label = "dynamic_preferences_users"

    def ready(self):
        UserPreferenceModel = self.get_model("UserPreferenceModel")

        preference_models.register(UserPreferenceModel, user_preferences_registry)
