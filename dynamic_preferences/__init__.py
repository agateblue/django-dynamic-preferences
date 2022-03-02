import django

__version__ = "1.12.0"

if django.VERSION < (3, 2):
    default_app_config = "dynamic_preferences.apps.DynamicPreferencesConfig"
