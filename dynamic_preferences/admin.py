from django.contrib import admin
from django import forms

from .settings import preferences_settings
from .registries import global_preferences_registry
from .models import GlobalPreferenceModel, UserPreferenceModel
from .forms import GlobalSinglePreferenceForm, UserSinglePreferenceForm, SinglePerInstancePreferenceForm


class DynamicPreferenceAdmin(admin.ModelAdmin):
    list_display = ('verbose_name', 'name', 'section', 'help_text', 'raw_value')
    readonly_fields = ('name', 'section')
    if preferences_settings.ADMIN_ENABLE_CHANGELIST_FORM:
        list_editable = ('raw_value',)
    search_fields = ['name', 'section', 'raw_value']
    list_filter = ('section',)

    if preferences_settings.ADMIN_ENABLE_CHANGELIST_FORM:
        def get_changelist_form(self, request, **kwargs):
            return self.changelist_form


class GlobalPreferenceAdmin(DynamicPreferenceAdmin):
    form = GlobalSinglePreferenceForm
    changelist_form = GlobalSinglePreferenceForm

    def get_queryset(self, *args, **kwargs):
        # Instanciate default prefs
        manager = global_preferences_registry.manager()
        manager.all()
        return super(GlobalPreferenceAdmin, self).get_queryset(*args, **kwargs)

admin.site.register(GlobalPreferenceModel, GlobalPreferenceAdmin)


class PerInstancePreferenceAdmin(DynamicPreferenceAdmin):
    list_display = ('instance',) + DynamicPreferenceAdmin.list_display
    raw_id_fields = ('instance',)
    form = SinglePerInstancePreferenceForm
    list_select_related = True

class UserPreferenceAdmin(PerInstancePreferenceAdmin):
    search_fields = ['instance__username'] + DynamicPreferenceAdmin.search_fields
    form = UserSinglePreferenceForm
    changelist_form = UserSinglePreferenceForm

    def get_queryset(self, request, *args, **kwargs):
        # Instanciate default prefs
        getattr(request.user, preferences_settings.MANAGER_ATTRIBUTE).all()
        return super(UserPreferenceAdmin, self).get_queryset(request, *args, **kwargs)

if preferences_settings.ENABLE_USER_PREFERENCES:
    admin.site.register(UserPreferenceModel, UserPreferenceAdmin)
