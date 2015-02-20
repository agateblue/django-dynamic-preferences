"""
Preference models, queryset and managers that handle the logic for persisting preferences.
"""

from django.db import models
from django.db.models.query import QuerySet
from .utils import update
from django.conf import settings
from django.utils.functional import cached_property
from dynamic_preferences.dynamic_preferences_registry import user_preference_registry, global_preference_registry
from dynamic_preferences.registries import preference_models



class PreferenceModelManager(models.Manager):

    def to_dict(self, **kwargs):
        """ 
            Return a dict of preference models values with the same structure as registries
            Used to access preferences value within templates
        """ 

        preferences = self.get_queryset().all()
        if kwargs: 
            preferences = preferences.filter(**kwargs)

        d = {}
        for p in preferences:
            try:
                d[p.section][p.name] = p.value
            except KeyError:
                d[p.section] = {}
                d[p.section][p.name] = p.value

        return d

class BasePreferenceModel(models.Model):
    """
    A base model with common logic for all preferences models.
    """

    #: The section under which the preference is declared
    section = models.TextField(max_length=255, db_index=True, blank=True, null=True, default=None)

    #: a name for the preference
    name = models.TextField(max_length=255, db_index=True)

    #: a value, serialized to a string. This field should not be accessed directly, use :py:attr:`BasePreferenceModel.value` instead
    raw_value = models.TextField(null=True, blank=True)

    #: Keep a reference to the whole preference registry.
    #: In order to map the Preference Model Instance to the Preference object.
    registry = None

    objects = PreferenceModelManager()

    class Meta:
        abstract = True
        app_label = 'dynamic_preferences'


    def __init__(self, *args, **kwargs):
        # Check if the model is already saved in DB
        v = kwargs.pop("value", None)
        super(BasePreferenceModel, self).__init__(*args, **kwargs)

        new = self.pk is None

        if new:
            if v is not None:
                self.value = v
            else:
                self.value = self.preference.default

    @cached_property
    def preference(self):
        return self.registry.get(section=self.section, name=self.name)

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

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '{0} - {1}/{2}: {3}'.format(self.__class__.__name__, self.section, self.name, self.value)

class GlobalPreferenceModel(BasePreferenceModel):

    class Meta:
        unique_together = ('section', 'name')
        app_label = 'dynamic_preferences'

        verbose_name = "global preference"
        verbose_name_plural = "global preferences"



class PerInstancePreferenceModel(BasePreferenceModel):
    """For preferences that are tied to a specific model instance"""
    #: the instance which is concerned by the preference
    #: use a ForeignKey pointing to the model of your choice 
    instance = None

    class Meta(BasePreferenceModel.Meta):
        unique_together = ('instance', 'section', 'name')
        abstract = True

class UserPreferenceModel(PerInstancePreferenceModel):

    instance = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="preferences")

    class Meta(PerInstancePreferenceModel.Meta):
        app_label = 'dynamic_preferences'
        verbose_name = "user preference"
        verbose_name_plural = "user preferences"

    @property
    def user(self):
        return self.instance
    @user.setter
    def user(self, value):
        self.instance = value
    

global_preferences = GlobalPreferenceModel.objects
user_preferences = UserPreferenceModel.objects





# Create default preferences for new instances

from django.db.models.signals import post_save

def create_default_per_instance_preferences(sender, created, instance, **kwargs): 
    """Create default preferences for PerInstancePreferenceModel"""
    
    if created:
        # we iterate throught registered preference models in order to get the instance class
        # and check if instance is and instance of this class
        for preference_model, registry in preference_models.items():
            instance_class = preference_model._meta.get_field('instance').related
            
            if isinstance(instance, instance_class):
                registry.create_default_preferences(instance)

post_save.connect(create_default_per_instance_preferences)