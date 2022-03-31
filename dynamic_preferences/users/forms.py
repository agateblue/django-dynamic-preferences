from six import string_types
from django import forms
from django.core.exceptions import ValidationError
from collections import OrderedDict

from .registries import user_preferences_registry
from ..forms import (
    SinglePerInstancePreferenceForm,
    preference_form_builder,
    PreferenceForm,
)
from ..exceptions import NotFoundInRegistry
from .models import UserPreferenceModel


class UserSinglePreferenceForm(SinglePerInstancePreferenceForm):
    class Meta:
        model = UserPreferenceModel
        fields = SinglePerInstancePreferenceForm.Meta.fields


def user_preference_form_builder(instance, preferences=[], **kwargs):
    """
    A shortcut :py:func:`preference_form_builder(UserPreferenceForm, preferences, **kwargs)`
    :param user: a :py:class:`django.contrib.auth.models.User` instance
    """
    return preference_form_builder(
        UserPreferenceForm, preferences, instance=instance, **kwargs
    )


class UserPreferenceForm(PreferenceForm):
    registry = user_preferences_registry
