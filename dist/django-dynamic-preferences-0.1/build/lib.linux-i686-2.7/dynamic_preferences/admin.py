from django.contrib import admin
from dynamic_preferences.models import GlobalPreferenceModel, UserPreferenceModel, SitePreferenceModel
from django import forms

class PreferenceChangeListForm(forms.ModelForm):
    """
    A form that integrate dynamic-preferences into django.contrib.admin
    """
    # Me must use an acutal model field, so we use raw_value. However, 
    # instance.value will be displayed in form.
    raw_value = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance')
        super(PreferenceChangeListForm, self).__init__(*args, **kwargs)
        
        self.fields['raw_value'] = self.instance.preference.setup_field()            

    def save(self, *args, **kwargs):
        self.cleaned_data['raw_value'] = self.instance.preference.serializer.serialize(self.cleaned_data['raw_value'])
        return super(PreferenceChangeListForm, self).save(*args, **kwargs)

class GlobalPreferenceChangeListForm(PreferenceChangeListForm):
    class Meta:
        model = GlobalPreferenceModel

class UserPreferenceChangeListForm(PreferenceChangeListForm):
    class Meta:
        model = UserPreferenceModel

class DynamicPreferenceAdmin(admin.ModelAdmin):
    readonly_fields = ('name', 'section', 'value')
    fields = ("raw_value",)
    list_display = ('name', 'section', 'raw_value')
    list_editable = ('raw_value',)
    search_fields = ['name', 'section', 'raw_value']
    list_filter = ('section',)
    
    def get_changelist_form(self, request, **kwargs):
        return self.changelist_form


class GlobalPreferenceAdmin(DynamicPreferenceAdmin):
    form = GlobalPreferenceChangeListForm
    changelist_form = GlobalPreferenceChangeListForm
    
        
admin.site.register(GlobalPreferenceModel, GlobalPreferenceAdmin)


class UserPreferenceAdmin(DynamicPreferenceAdmin):
    form = UserPreferenceChangeListForm
    list_display = ('user',) + DynamicPreferenceAdmin.list_display
    search_fields = ['user__username'] + DynamicPreferenceAdmin.search_fields
    changelist_form = UserPreferenceChangeListForm
        
admin.site.register(UserPreferenceModel, UserPreferenceAdmin)
