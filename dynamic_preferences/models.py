"""
Preference models, queryset and managers that handle the logic for persisting preferences.
"""

from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
from django.utils.functional import cached_property

from dynamic_preferences.registries import preference_models, user_preferences_registry, global_preferences_registry
from .utils import update


class BasePreferenceModel(models.Model):

    """
    A base model with common logic for all preferences models.
    """

    #: The section under which the preference is declared
    section = models.CharField(
        max_length=150, db_index=True, blank=True, null=True, default=None)

    #: a name for the preference
    name = models.CharField(max_length=150, db_index=True)

    #: a value, serialized to a string. This field should not be accessed directly, use :py:attr:`BasePreferenceModel.value` instead
    raw_value = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
        app_label = 'dynamic_preferences'

    @cached_property
    def preference(self):
        return self.registry.get(section=self.section, name=self.name)

    @property
    def verbose_name(self):
        return self.preference.get('verbose_name', self.preference.identifier)

    @property
    def help_text(self):
        return self.preference.get('help_text', '')

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

    def save(self, **kwargs):

        if self.pk is None and not self.raw_value:

                self.value = self.preference.default
        super(BasePreferenceModel, self).save(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '{0} - {1}/{2}'.format(self.__class__.__name__, self.section, self.name)


class GlobalPreferenceModel(BasePreferenceModel):

    registry = global_preferences_registry

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

    @classmethod
    def get_instance_model(cls):
        return cls._meta.get_field('instance').rel.to

    @property
    def registry(self):
        return preference_models.get_by_instance(self.instance)


class UserPreferenceModel(PerInstancePreferenceModel):

    instance = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta(PerInstancePreferenceModel.Meta):
        app_label = 'dynamic_preferences'
        verbose_name = "user preference"
        verbose_name_plural = "user preferences"


global_preferences_registry.preference_model = GlobalPreferenceModel

# Create default preferences for new instances

from django.db.models.signals import post_save


def create_default_per_instance_preferences(sender, created, instance, **kwargs):
    """Create default preferences for PerInstancePreferenceModel"""

    if created:
        try:
            registry = preference_models.get_by_instance(instance)
            registry.create_default_preferences(instance)
        except AttributeError:
            pass


def invalidate_cache(sender, created, instance, **kwargs):
    if not isinstance(instance, BasePreferenceModel):
        return
    registry = preference_models.get_by_preference(instance)
    linked_instance = getattr(instance, 'instance', None)
    kwargs = {}
    if linked_instance:
        kwargs['instance'] = linked_instance

    manager = registry.manager(**kwargs)
    manager.to_cache(instance)

post_save.connect(create_default_per_instance_preferences)
post_save.connect(invalidate_cache)
