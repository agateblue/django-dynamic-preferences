from django.contrib import admin
from dynamic_preferences.models import GlobalPreferenceModel, UserPreferenceModel, SitePreferenceModel
from django import forms

class GlobalPreferenceForm(forms.ModelForm):
    class Meta:
        model = GlobalPreferenceModel



class GlobalPreferenceAdmin(admin.ModelAdmin):
    form = GlobalPreferenceForm
    fields = ('app', 'name', "raw_value")
    list_display = ('name', 'app', 'value')

    def queryset(self, request):
        qs = super(GlobalPreferenceAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return
admin.site.register(GlobalPreferenceModel, GlobalPreferenceAdmin)
