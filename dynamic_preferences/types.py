"""
    Class defined here are used by dynamic_preferences.preferences to specify
    preferences types (Bool, int, etc.) and rules according validation

"""
import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import CharField, IntegerField, BooleanField, ChoiceField, DateTimeField, TypedChoiceField
from django.utils.functional import cached_property

from .preferences import AbstractPreference
from dynamic_preferences.serializers import *

class BasePreferenceType(AbstractPreference):

    # A form field that will be used to display and edit the preference
    # use a class, not an instance
    field_class = None

    # these default will merged with ones from field_attributes
    # then pass to class provided in field in order to instantiate the actual field

    _default_field_attributes = {
        "required": True,
    }

    # Override this attribute to change field behaviour
    field_attributes = {}

    # A serializer class (see dynamic_preferences.serializers)
    serializer = None

    _field = None

    def get_field_kwargs(self):
        field_kwargs = dict(self._default_field_attributes)

        try:
            field_kwargs['initial'] = self.initial
        except AttributeError:
            pass
        field_kwargs.update(self.field_attributes)
        return field_kwargs

    @property
    def initial(self):
        """
        :return: initial data for form field, from field_attribute['initial'], _default_field_attribute['initial'] or
         default
        """
        return self.field_attributes.get('initial', self._default_field_attributes.get('initial', self.default))

    @property
    def field(self):
        return self.setup_field()

    def setup_field(self, **kwargs):
        """
            Create an actual instance of self.field
            Override this method if needed
        """
        field_class = self.get('field_class')
        field_kwargs = self.get_field_kwargs()
        field_kwargs.update(kwargs)
        return field_class(**field_kwargs)

    def get_field_kwargs(self):
        kwargs = {}
        kwargs['label'] = self.get('verbose_name')
        kwargs['widget'] = self.get('widget')
        kwargs['initial'] = self.get('default')
        return kwargs

class BooleanPreference(BasePreferenceType):

    field_class = BooleanField
    serializer = BooleanSerializer

    def get_field_kwargs(self):
        kwargs = super(BooleanPreference, self).get_field_kwargs()
        kwargs['required'] = False
        return kwargs

class IntPreference(BasePreferenceType):

    field_class = IntegerField
    serializer = IntSerializer


class StringPreference(BasePreferenceType):

    field_class = CharField
    serializer = StringSerializer

class LongStringPreference(StringPreference):
    _default_field_attributes = {
        "widget": forms.Textarea,
    }

class ChoicePreference(BasePreferenceType):

    choices = ()
    field_class = ChoiceField
    serializer = StringSerializer

    def get_field_kwargs(self):
        field_kwargs = super(ChoicePreference, self).get_field_kwargs()

        field_kwargs['choices'] = self.choices or self.field_attribute['initial']
        return field_kwargs
