from django.contrib import admin as django_admin
from django import forms

from ..settings import preferences_settings
from .. import admin
from .models import UserPreferenceModel
from .forms import UserSinglePreferenceForm


class UserPreferenceAdmin(admin.PerInstancePreferenceAdmin):
    search_fields = ['instance__username'] + admin.DynamicPreferenceAdmin.search_fields
    form = UserSinglePreferenceForm
    changelist_form = UserSinglePreferenceForm

    def get_queryset(self, request, *args, **kwargs):
        # Instanciate default prefs
        getattr(request.user, preferences_settings.MANAGER_ATTRIBUTE).all()
        return super(UserPreferenceAdmin, self).get_queryset(
            request, *args, **kwargs)


django_admin.site.register(UserPreferenceModel, UserPreferenceAdmin)
