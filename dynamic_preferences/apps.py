from django.apps import AppConfig
from django.contrib.auth import get_user_model

from .registries import autodiscover
from .models import GlobalPreferenceModel, UserPreferenceModel, per_instance_preferences
from .preferences import GlobalPreference, UserPreference


class DynamicPreferencesConfig(AppConfig):
    name = 'dynamic_preferences'
    verbose_name = "Dynamic Preferences"

    def ready(self):
        per_instance_preferences.register(get_user_model(), UserPreference)
        autodiscover()