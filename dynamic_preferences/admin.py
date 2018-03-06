from django.contrib import admin
from django import forms

from .settings import preferences_settings
from .registries import global_preferences_registry
from .models import GlobalPreferenceModel
from .forms import GlobalSinglePreferenceForm, SinglePerInstancePreferenceForm


class SectionFilter(admin.AllValuesFieldListFilter):

    def __init__(self, field, request, params, model, model_admin, field_path):
        super(SectionFilter, self).__init__(field, request, params, model, model_admin, field_path)
        parent_model, reverse_path = admin.utils.reverse_field_path(model, field_path)
        if model == parent_model:
            queryset = model_admin.get_queryset(request)
        else:
            queryset = parent_model._default_manager.all()
        self.registries = []
        registry_name_set = set()
        for preferenceModel in queryset.distinct():
            l = len(registry_name_set)
            registry_name_set.add(preferenceModel.registry.__class__.__name__)
            if len(registry_name_set) != l:
                self.registries.append(preferenceModel.registry)
        

    def choices(self, changelist):
        choices = super(SectionFilter, self).choices(changelist)
        for choice in choices:
            display = choice['display']
            try:
                for registry in self.registries:
                    display = registry.section_objects[display].verbose_name
                choice["display"] = display
            except (KeyError):
                pass
            yield choice


class DynamicPreferenceAdmin(admin.ModelAdmin):
    list_display = ('verbose_name', 'name', 'section_name', 'help_text', 'raw_value')
    fields = ('raw_value', 'name', 'section_name')
    readonly_fields = ('name', 'section_name')
    if preferences_settings.ADMIN_ENABLE_CHANGELIST_FORM:
        list_editable = ('raw_value',)
    search_fields = ['name', 'section', 'raw_value']
    list_filter = (('section',  SectionFilter),)

    if preferences_settings.ADMIN_ENABLE_CHANGELIST_FORM:
        def get_changelist_form(self, request, **kwargs):
            return self.changelist_form

    def section_name(self, obj):
        try:
            return obj.registry.section_objects[obj.section].verbose_name
        except KeyError:
            pass
        return obj.section


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
    fields = ('instance',) + DynamicPreferenceAdmin.fields
    raw_id_fields = ('instance',)
    form = SinglePerInstancePreferenceForm
    changelist_form = SinglePerInstancePreferenceForm
    list_select_related = True
