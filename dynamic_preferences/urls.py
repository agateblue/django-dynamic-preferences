from django.conf.urls import patterns, include, url
from django.contrib.admin.views.decorators import staff_member_required
from dynamic_preferences import views
from registries import user_preferences_registry, global_preferences_registry
from forms import GlobalPreferenceForm
urlpatterns = patterns('',

    url(r'^global$', views.PreferenceFormView.as_view(registry=global_preferences_registry, form_class=GlobalPreferenceForm), name="dynamic_preferences.global"),
    url(r'^global/(?P<section>\w+)$', views.PreferenceFormView.as_view(registry=global_preferences_registry, form_class=GlobalPreferenceForm), name="dynamic_preferences.global.section"),
)
