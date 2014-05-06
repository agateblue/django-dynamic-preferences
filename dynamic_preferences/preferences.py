"""
    Preferences are regular Python objects that can be declared within a django app
    Once declared and registered, they can be edited by admins (for SitePreference)
    and regular Users (for UserPreference)

    UserPreference and SitePreference are mapped to django models UserPreferenceModel
    and SitePreferenceModel, which store the actual values for each user/site.

"""
from registries import user_preferences, site_preferences
from dynamic_preferences.models import SitePreferenceModel, UserPreferenceModel

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

    def to_model(self):
        """
            Save a PreferenceModel instance corresponding to the given model in database
        """

        raise NotImplementedError


class UserPreference(BasePreference):

    registry = user_preferences
    model = UserPreferenceModel

    def to_model(self, user, value=None):

        try:
            preference = self.model.objects.get(
                app=self.app,
                name=self.name,
                user=user,
            )

        except self.model.DoesNotExist:
            preference = self.model(
                app=self.app,
                name=self.name,
                user=user,
                value=value
            )
            preference.save()

        return preference


class SitePreference(BasePreference):

    registry = site_preferences
    model = SitePreferenceModel

    def to_model(self, site, value=None):

        try:
            preference = self.model.objects.get(
                app=self.app,
                name=self.name,
                site=site,
            )

        except self.model.DoesNotExist:
            preference = self.model(
                app=self.app,
                name=self.name,
                site=site,
                value=value
            )
            preference.save()

        return preference