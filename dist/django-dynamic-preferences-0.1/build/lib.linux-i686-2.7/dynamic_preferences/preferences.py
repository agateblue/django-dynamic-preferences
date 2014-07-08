"""
Preferences are regular Python objects that can be declared within any django app.
Once declared and registered, they can be edited by admins (for :py:class:`SitePreference` and :py:class:`GlobalPreference`)
and regular Users (for :py:class:`UserPreference`)

UserPreference, SitePreference and GlobalPreference are mapped to corresponding PreferenceModel,
which store the actual values.

"""
from registries import user_preferences_registry, site_preferences_registry, global_preferences_registry
from dynamic_preferences.models import SitePreferenceModel, UserPreferenceModel, GlobalPreferenceModel


class BasePreference(object):
    """
    A base class that handle common logic  for preferences
    """

    #: The registry in which preference will be registered (:py:const:`registries.global_preferences`, :py:const:`registries.site_preferences` or :py:const:`registries.user_preferences`)
    registry = None

    #: The section under which the preference will be registered
    section = None

    #: The preference name
    name = ""

    #: A default value for the preference
    default = None

    #: The model corresponding to this preference type (:py:class:`SitePreference`, :py:class:`GlobalPreference` or :py:class:`UserPreference`)
    model = None

    def register(self):
        self.registry.register(name=self.name, section=self.section, preference=self)

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
        return unicode(separator.join([section, self.name]))

class GlobalPreference(BasePreference):
    """
        A preference that apply to a whole django installation
    """

    registry = global_preferences_registry
    model = GlobalPreferenceModel


class UserPreference(BasePreference):
    """
    Preference that is tied to a :py:class:`django.contrib.auth.models.User` instance
    """

    registry = user_preferences_registry
    model = UserPreferenceModel


class SitePreference(BasePreference):
    """
        Preference for each django.contrib.site
    """
    registry = site_preferences_registry
    model = SitePreferenceModel
