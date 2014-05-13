from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models.query import QuerySet
from utils import update
from dynamic_preferences.registries import user_preferences, site_preferences, global_preferences



class PreferenceSite(Site):

    class Meta:
        proxy = True

class PreferenceUser(User):
    class Meta:
            proxy = True


class BasePreferenceModel(models.Model):

    # The app under which the app is declared
    app = models.TextField(max_length=255, db_index=True)

    # a name for the preference
    name = models.TextField(max_length=255, db_index=True)

    # a value, serialized to a string
    # this field should not be accessed directly, use value instead
    raw_value = models.TextField(null=True, blank=True)

    # Keep a reference to the whole preference registry
    # In order to map the Preference Model Instance to the Preference object
    registry = None

    # Will be set in __init__
    preference = None

    def __init__(self, *args, **kwargs):
        # Check if the model is already saved in DB

        v = kwargs.pop("value", None)

        super(BasePreferenceModel, self).__init__(*args, **kwargs)

        new = self.pk is None
        self.preference = self.registry.get(app=self.app, name=self.name)
        if new:
            if v is not None:
                self.value = v
            else:
                self.value = self.preference.default

    class Meta:
        abstract = True

    def set_value(self, value):
        """
            Save serialized self.value to self.raw_value
        """
        self.raw_value = self.preference.serializer.serialize(value)

    def get_value(self):
        """
            Return deserialized self.raw_value
        """
        return self.preference.serializer.deserialize(self.raw_value)

    value = property(get_value, set_value)


class GlobalPreferenceModel(BasePreferenceModel):

    registry = global_preferences

    class Meta:
        unique_together = ('app', 'name')


class UserPreferenceModel(BasePreferenceModel):

    user = models.ForeignKey(User, related_name="preferences")
    registry = user_preferences

    class Meta:
        unique_together = ('user', 'app', 'name')


class SitePreferenceModel(BasePreferenceModel):

    site = models.ForeignKey(Site, related_name="preferences")
    registry = site_preferences

    class Meta:
        unique_together = ('site', 'app', 'name')