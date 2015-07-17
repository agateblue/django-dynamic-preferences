

class DynamicPreferencesException(Exception):
    detail_default = 'An exception occurred with django-dynamic-preferences'

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = str(detail)
        else:
            self.detail = str(self.detail_default)

    def __str__(self):
        return self.detail

class MissingDefault(DynamicPreferencesException):
    detail_default = 'You must provide a default value for all preferences'
    
class NotFoundInRegistry(DynamicPreferencesException, KeyError):
    detail_default = 'Preference with this name/section not found in registry'

class DoesNotExist(DynamicPreferencesException):
    detail_default = 'Cannot retrieve preference value, ensure the preference is correctly registered and database is synced'

class CachedValueNotFound(DynamicPreferencesException):
    detail_default = 'Cached value not found'
