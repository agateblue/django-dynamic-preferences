"""
    Preferences are regular Python objects that can be declared within a django app
    Once declared and registered, they can be edited by admins (for SitePreference and GlobalPreference)
    and regular Users (for UserPreference)

    UserPreference, SitePreference and GlobalPreference are mapped to corresponding *PreferenceModel,
    which store the actual values.

"""
from registries import user_preferences, site_preferences, global_preferences
from dynamic_preferences.models import SitePreferenceModel, UserPreferenceModel, GlobalPreferenceModel

class BasePreference:

    # The registry in which settings are stored
    registry = None

    app = None
    name = ""
    value = None
    default = None

    # Django model corresponding to this Preference
    model = None

    def register(self):
        self.registry.register(self.app, self.name, self)

    def to_model(self, **kwargs):
        """
            Save a PreferenceModel instance corresponding to the given model in database
        """
        value = kwargs.pop('value', None)

        try:
            preference = self.model.objects.get(
                app=self.app,
                name=self.name,
                **kwargs
            )

        except self.model.DoesNotExist:
            preference = self.model(
                app=self.app,
                name=self.name,
                value=value,
                **kwargs
            )
            preference.save()

        return preference


class GlobalPreference(BasePreference):
    """
        A preference that apply to a whole django installation
    """

    registry = global_preferences
    model = GlobalPreferenceModel


class UserPreference(BasePreference):
    """
        Preference for each user
    """

    registry = user_preferences
    model = UserPreferenceModel


class SitePreference(BasePreference):
    """
        Preference for each django.contrib.site
    """
    registry = site_preferences
    model = SitePreferenceModel
