"""
Preferences are regular Python objects that can be declared within any django app.
Once declared and registered, they can be edited by admins (for :py:class:`SitePreference` and :py:class:`GlobalPreference`)
and regular Users (for :py:class:`UserPreference`)

UserPreference, SitePreference and GlobalPreference are mapped to corresponding PreferenceModel,
which store the actual values.

"""
from __future__ import unicode_literals
import re
import warnings

from .settings import preferences_settings
from .exceptions import MissingDefault
from .serializers import UNSET


class InvalidNameError(ValueError):
    pass


def check_name(name, obj):
    error = None
    if not re.match("^\w+$", name):
        error = "Non-alphanumeric / underscore characters are forbidden in section and preferences names"
    if preferences_settings.SECTION_KEY_SEPARATOR in name:
        error = 'Sequence "{0}" is forbidden in section and preferences name, since it is used to access values via managers'.format(
            preferences_settings.SECTION_KEY_SEPARATOR
        )

    if error:
        full_message = 'Invalid name "{0}" while instanciating {1} object: {2}'.format(
            name, obj, error
        )
        raise InvalidNameError(full_message)


class Section(object):
    def __init__(self, name, verbose_name=None):
        self.name = name
        self.verbose_name = verbose_name or name
        if preferences_settings.VALIDATE_NAMES and name:
            check_name(self.name, self)

    def __str__(self):
        if not self.verbose_name:
            return ""
        return str(self.verbose_name)


EMPTY_SECTION = Section(None)


class AbstractPreference(object):
    """
    A base class that handle common logic for preferences
    """

    #: The section under which the preference will be registered
    section = EMPTY_SECTION

    #: The preference name
    name = ""

    #: A default value for the preference
    default = UNSET

    def __init__(self, registry=None):
        if preferences_settings.VALIDATE_NAMES:
            check_name(self.name, self)
        if self.section and not hasattr(self.section, "name"):
            self.section = Section(name=self.section)
            warnings.warn(
                "Implicit section instanciation is deprecated and "
                "will be removed in future versions of django-dynamic-preferences",
                DeprecationWarning,
                stacklevel=2,
            )

        self.registry = registry
        if self.default == UNSET and not getattr(self, "get_default", None):
            raise MissingDefault

    def get(self, attr, default=None):
        getter = "get_{0}".format(attr)
        if hasattr(self, getter):
            return getattr(self, getter)()
        return getattr(self, attr, default)

    @property
    def model(self):
        return self.registry.preference_model

    def identifier(self):
        """
        Return the name and the section of the Preference joined with a separator, with the form `section<separator>name`
        """

        if not self.section or not self.section.name:
            return self.name
        return preferences_settings.SECTION_KEY_SEPARATOR.join(
            [self.section.name, self.name]
        )
