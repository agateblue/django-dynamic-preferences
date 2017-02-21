from six import string_types
from django import forms
from django.core.exceptions import ValidationError
from collections import OrderedDict

from .registries import global_preferences_registry
from .models import GlobalPreferenceModel
from .exceptions import NotFoundInRegistry


class AbstractSinglePreferenceForm(forms.ModelForm):

    class Meta:
        fields = ('section', 'name', 'raw_value')

    def __init__(self, *args, **kwargs):

        self.instance = kwargs.get('instance')
        initial = {}
        if self.instance:
            initial['raw_value'] = self.instance.value
            kwargs['initial'] = initial
        super(AbstractSinglePreferenceForm, self).__init__(*args, **kwargs)

        if self.instance.name:
            self.fields['raw_value'] = self.instance.preference.setup_field()


    def clean(self):
        cleaned_data = super(AbstractSinglePreferenceForm, self).clean()
        try:
            self.instance.name, self.instance.section = cleaned_data['name'], cleaned_data['section']
        except KeyError: # changelist form
            pass
        try:
            self.instance.preference
        except NotFoundInRegistry:
            raise ValidationError(NotFoundInRegistry.detail_default)
        return self.cleaned_data

    def save(self, *args, **kwargs):
        self.instance.value = self.cleaned_data['raw_value']
        return super(AbstractSinglePreferenceForm, self).save(*args, **kwargs)

class SinglePerInstancePreferenceForm(AbstractSinglePreferenceForm):

    class Meta:
        fields = ('instance',) + AbstractSinglePreferenceForm.Meta.fields

    def clean(self):
        cleaned_data = super(AbstractSinglePreferenceForm, self).clean()
        try:
            self.instance.name, self.instance.section = cleaned_data['name'], cleaned_data['section']
        except KeyError: # changelist form
            pass
        i = cleaned_data.get('instance')
        if i:
            self.instance.instance = i
            try:
                self.instance.preference
            except NotFoundInRegistry:
                raise ValidationError(NotFoundInRegistry.detail_default)
        return self.cleaned_data

class GlobalSinglePreferenceForm(AbstractSinglePreferenceForm):

    class Meta:
        model = GlobalPreferenceModel
        fields = AbstractSinglePreferenceForm.Meta.fields


def preference_form_builder(form_base_class, preferences=[], **kwargs):
    """
    Return a form class for updating preferences
    :param form_base_class: a Form class used as the base. Must have a ``registry` attribute
    :param preferences: a list of :py:class:
    :param section: a section where the form builder will load preferences
    """
    registry = form_base_class.registry
    preferences_obj = []
    if len(preferences) > 0:
        # Preferences have been selected explicitly
        for pref in preferences:
            if isinstance(pref, string_types):
                preferences_obj.append(registry.get(name=pref))
            elif type(pref) == tuple:
                preferences_obj.append(
                    registry.get(name=pref[0], section=pref[1]))
            else:
                raise NotImplementedError(
                    "The data you provide can't be converted to a Preference object")
    elif kwargs.get('section', None):
        # Try to use section param
        preferences_obj = registry.preferences(
            section=kwargs.get('section', None))

    else:
        # display all preferences in the form
        preferences_obj = registry.preferences()

    fields = OrderedDict()
    instances = []
    model_kwargs = kwargs.get('model', {})
    manager = registry.manager(**model_kwargs)

    for preference in preferences_obj:
        f = preference.field
        instance = manager.get_db_pref(
            section=preference.section.name, name=preference.name)
        f.initial = instance.value
        fields[preference.identifier()] = f
        instances.append(instance)

    form_class = type(
        'Custom' + form_base_class.__name__, (form_base_class,), {})
    form_class.base_fields = fields
    form_class.preferences = preferences_obj
    form_class.instances = instances
    return form_class


def global_preference_form_builder(preferences=[], **kwargs):
    """
    A shortcut :py:func:`preference_form_builder(GlobalPreferenceForm, preferences, **kwargs)`
    """
    return preference_form_builder(GlobalPreferenceForm, preferences, **kwargs)


class PreferenceForm(forms.Form):

    registry = None

    def update_preferences(self, **kwargs):
        for instance in self.instances:
            instance.value = self.cleaned_data[
                instance.preference.identifier()]
            instance.save()


class GlobalPreferenceForm(PreferenceForm):

    registry = global_preferences_registry
