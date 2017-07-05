# Taken from django-rest-framework
# https://github.com/tomchristie/django-rest-framework
# Copyright (c) 2011-2015, Tom Christie All rights reserved.

from django.conf import settings

SETTINGS_ATTR = 'DYNAMIC_PREFERENCES'
USER_SETTINGS = None



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
    'ENABLE_USER_PREFERENCES': True,
    'ENABLE_CACHE': True,
    'VALIDATE_NAMES': True,
    'FILE_PREFERENCE_UPLOAD_DIR': 'dynamic_preferences',
    # this will be used to cache empty values, since some cache backends
    # does not support it on get_many
    'CACHE_NONE_VALUE': '__dynamic_preferences_empty_value'
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
    def __init__(self, defaults=None):
        self.defaults = defaults or DEFAULTS

    @property
    def user_settings(self):
        return getattr(settings, SETTINGS_ATTR, {})

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
        # We sometimes need to bypass that, like in tests
        if getattr(settings, 'CACHE_DYNAMIC_PREFERENCES_SETTINGS', True):
            setattr(self, attr, val)
        return val


preferences_settings = PreferenceSettings(DEFAULTS)
