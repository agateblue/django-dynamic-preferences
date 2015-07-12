"""
Preferences are regular Python objects that can be declared within any django app.
Once declared and registered, they can be edited by admins (for :py:class:`SitePreference` and :py:class:`GlobalPreference`)
and regular Users (for :py:class:`UserPreference`)

UserPreference, SitePreference and GlobalPreference are mapped to corresponding PreferenceModel,
which store the actual values.

"""
from __future__ import unicode_literals

from .settings import preferences_settings
from .exceptions import MissingDefault

class Unset(object):
    pass

class AbstractPreference(object):
    """
    A base class that handle common logic for preferences
    """

    #: The section under which the preference will be registered
    section = None

    #: The preference name
    name = ""

    #: A default value for the preference
    default = Unset

    #: The model corresponding to this preference type (:py:class:`SitePreference`, :py:class:`GlobalPreference` or :py:class:`UserPreference`)
    model = None

    def __init__(self, registry=None):
        self.registry = registry
        if self.default == Unset:
            raise MissingDefault

    @property
    def model(self):
        return self.registry.preference_model

    def identifier(self):
        """
        Return the name and the section of the Preference joined with a separator, with the form `section<separator>name`
        """
        section = self.section or ''
        if not section:
            return self.name
        return preferences_settings.SECTION_KEY_SEPARATOR.join([section, self.name])
