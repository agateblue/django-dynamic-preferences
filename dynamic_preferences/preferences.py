"""
Preferences are regular Python objects that can be declared within any django app.
Once declared and registered, they can be edited by admins (for :py:class:`SitePreference` and :py:class:`GlobalPreference`)
and regular Users (for :py:class:`UserPreference`)

UserPreference, SitePreference and GlobalPreference are mapped to corresponding PreferenceModel,
which store the actual values.

"""
from __future__ import unicode_literals


class AbstractPreference(object):
    """
    A base class that handle common logic for preferences
    """

    #: The section under which the preference will be registered
    section = None

    #: The preference name
    name = ""

    #: A default value for the preference
    default = None

    #: The model corresponding to this preference type (:py:class:`SitePreference`, :py:class:`GlobalPreference` or :py:class:`UserPreference`)
    model = None

    def __init__(self, registry=None):
        self.registry = registry
        
    @property
    def model(self):
        return self.registry.preference_model

    def to_model(self, **kwargs):
        """
        Retrieve a model instance corresponding to the Preference in database.
        This method will create the model instance if needed.


        :param kwargs: Keyword arguments that will be passed directly to queryset or new model
        :return: a :py:class:`models.BasePreferenceModel` instance
        """

        value = kwargs.pop('value', None)

        try:
            preference = self.model.objects.get(
                section=self.section,
                name=self.name,
                **kwargs
            )

        except self.model.DoesNotExist:
            
            preference = self.model(
                section=self.section,
                name=self.name,
                value=value,
                **kwargs
            )
            preference.save()

        return preference

    def identifier(self, separator="."):
        """
        Return the name and the section of the Preference joined with a separator, with the form `section<separator>name`
        """
        section = self.section or ""
        return separator.join([section, self.name])
