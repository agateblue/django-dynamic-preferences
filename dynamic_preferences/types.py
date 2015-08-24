"""
    Class defined here are used by dynamic_preferences.preferences to specify
    preferences types (Bool, int, etc.) and rules according validation

"""
import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from .preferences import AbstractPreference
from dynamic_preferences.serializers import *

class BasePreferenceType(AbstractPreference):

    # A form field that will be used to display and edit the preference
    # use a class, not an instance
    field_class = None

    # Override this attribute to change field behaviour
    field_attributes = {}

    # A serializer class (see dynamic_preferences.serializers)
    serializer = None

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
        kwargs['help_text'] = self.get('help_text')
        kwargs['widget'] = self.get('widget')
        kwargs['initial'] = self.get('default')
        return kwargs

class BooleanPreference(BasePreferenceType):

    field_class = forms.BooleanField
    serializer = BooleanSerializer

    def get_field_kwargs(self):
        kwargs = super(BooleanPreference, self).get_field_kwargs()
        kwargs['required'] = False
        return kwargs

class IntegerPreference(BasePreferenceType):

    field_class = forms.IntegerField
    serializer = IntegerSerializer

IntPreference = IntegerPreference

class StringPreference(BasePreferenceType):

    field_class = forms.CharField
    serializer = StringSerializer

class LongStringPreference(StringPreference):
    widget = forms.Textarea

class ChoicePreference(BasePreferenceType):

    choices = ()
    field_class = forms.ChoiceField
    serializer = StringSerializer

    def get_field_kwargs(self):
        field_kwargs = super(ChoicePreference, self).get_field_kwargs()

        field_kwargs['choices'] = self.choices or self.field_attribute['initial']
        return field_kwargs
