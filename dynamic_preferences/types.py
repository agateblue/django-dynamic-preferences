"""
    Class defined here are used by dynamic_preferences.preferences to specify
    preferences types (Bool, int, etc.) and rules according validation

"""
import datetime
from django import forms
from django.db.models.signals import pre_delete
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

from .preferences import AbstractPreference, Section
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


class DecimalPreference(BasePreferenceType):
    field_class = forms.DecimalField
    serializer = DecimalSerializer


class FloatPreference(BasePreferenceType):
    field_class = forms.FloatField
    serializer = FloatSerializer


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


def create_deletion_handler(preference):
    """Will generate a dynamic handler to purge related preference on instance deletion"""

    def delete_related_preferences(sender, instance, *args, **kwargs):
        queryset = preference.registry.preference_model.objects \
            .filter(name=preference.name,
                    section=preference.section)
        related_preferences = queryset.filter(raw_value=preference.serializer.serialize(instance))
        related_preferences.delete()

    return delete_related_preferences


class ModelChoicePreference(BasePreferenceType):
    field_class = forms.ModelChoiceField
    serializer_class = ModelSerializer
    model = None
    queryset = None
    signals_handlers = {}

    def __init__(self, *args, **kwargs):
        super(ModelChoicePreference, self).__init__(*args, **kwargs)
        self.model = self.model or self.queryset.model
        if not hasattr(self, 'queryset'):
            self.queryset = self.model.objects.all()

        self.serializer = ModelSerializer(self.model)

        self._setup_signals()

    def _setup_signals(self):
        handler = create_deletion_handler(self)
        # We need to keep a reference to the handler or it will cause
        # weakref to die and our handler will not be called
        self.signals_handlers['pre_delete'] = [handler]
        pre_delete.connect(handler, sender=self.model)

    def get_field_kwargs(self):
        kw = super(ModelChoicePreference, self).get_field_kwargs()
        kw['queryset'] = self.get('queryset')
        return kw


class OptimisedClearableFileInput(forms.ClearableFileInput):
    template_with_initial = (
        '%(initial_text)s: <a href="%(initial_url)s">%(initial)s</a> <br>'
        '<span class="clear-file"> %(clear_template)s</span> <span>%(input_text)s: %(input)s </span>'
    )

    clear_checkbox_label = ugettext_lazy('Remove this file')

    template_with_clear = '%(clear)s %(clear_checkbox_label)s -'

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = '%(input)s'
        substitutions['input'] = super(forms.ClearableFileInput, self).render(name, value, attrs)

        if self.is_initial(value):
            template = self.template_with_initial
            substitutions.update(self.get_template_substitution_values(value))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = '<input type="checkbox" id="%(id)s" name="%(name)s">' % {
                    'id': substitutions['clear_checkbox_id'],
                    'name': substitutions['clear_checkbox_name'],
                }
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)


class FilePreference(BasePreferenceType):
    field_class = forms.FileField
    # this is to fix the ClearableFileInput not to use labels for the clear checkbox as this seems to be incompatible
    # with Django admin forms.css. In my opinion the forms.ClearableFileInput html is not optimal.
    widget = OptimisedClearableFileInput
    serializer = FileSerializer

    def get_field_kwargs(self):
        kwargs = super(FilePreference, self).get_field_kwargs()
        kwargs['required'] = self.get('required', False)
        return kwargs
