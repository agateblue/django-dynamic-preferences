# Taken from django-rest-framework
# https://github.com/tomchristie/django-rest-framework
# Copyright (c) 2011-2015, Tom Christie All rights reserved.

SETTINGS_ATTR = 'DYNAMIC_PREFERENCES'
USER_SETTINGS = None

try:
    from django.conf import settings
except ImportError:
    pass
else:
    # Only pull Django settings if Django environment variable exists.
    if settings.configured:
        USER_SETTINGS = getattr(settings, SETTINGS_ATTR, None)


DEFAULTS = {
    # 'REGISTRY_MODULE': 'prefs',
    # 'BASE_PREFIX': 'base',
    # 'SECTIONS_PREFIX': 'sections',
    # 'PREFERENCES_PREFIX': 'preferences',
    # 'PERMISSIONS_PREFIX': 'permissions',
    'MANAGER_ATTRIBUTE': 'preferences',
    'SECTION_KEY_SEPARATOR': '__',
    'REGISTRY_MODULE': 'dynamic_preferences_registry',
    'ADMIN_ENABLE_CHANGELIST_FORM': False,
}


class PreferenceSettings(object):
    """
    A settings object, that allows API settings to be accessed as properties.
    For example:

        from rest_framework.settings import api_settings
        print(api_settings.DEFAULT_RENDERER_CLASSES)

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """
    def __init__(self, user_settings=None, defaults=None):
        self.user_settings = user_settings or {}
        self.defaults = defaults or DEFAULTS

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid preference setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        setattr(self, attr, val)
        return val


preferences_settings = PreferenceSettings(USER_SETTINGS, DEFAULTS)
