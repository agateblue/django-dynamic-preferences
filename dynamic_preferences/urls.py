from django.conf.urls import patterns, include, url
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from . import views
from . import global_preferences
from .forms import GlobalPreferenceForm


urlpatterns = patterns('',

    url(r'^global/$', 
        staff_member_required(views.PreferenceFormView.as_view(
            registry=global_preferences, 
            form_class=GlobalPreferenceForm)), 
        name="dynamic_preferences.global"),
    url(r'^global/(?P<section>\w+)$', 
        staff_member_required(views.PreferenceFormView.as_view(
            registry=global_preferences, 
            form_class=GlobalPreferenceForm)), 
        name="dynamic_preferences.global.section"),

    url(r'^user/$', 
        login_required(views.UserPreferenceFormView.as_view()), 
        name="dynamic_preferences.user"),
    url(r'^user/(?P<section>\w+)$', 
        login_required(views.UserPreferenceFormView.as_view()), 
        name="dynamic_preferences.user.section"),
)


