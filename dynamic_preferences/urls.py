from django.conf.urls import patterns, include, url
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from dynamic_preferences import views
from registries import user_preferences_registry, global_preferences_registry
from forms import GlobalPreferenceForm

from django.conf import settings

test = False
try:
    test = settings.TESTING
except:
    pass

urlpatterns = patterns('',

    url(r'^global/$', 
        staff_member_required(views.PreferenceFormView.as_view(
            registry=global_preferences_registry, 
            form_class=GlobalPreferenceForm)), 
        name="dynamic_preferences.global"),
    url(r'^global/(?P<section>\w+)$', 
        staff_member_required(views.PreferenceFormView.as_view(
            registry=global_preferences_registry, 
            form_class=GlobalPreferenceForm)), 
        name="dynamic_preferences.global.section"),

    url(r'^user/$', 
        login_required(views.UserPreferenceFormView.as_view()), 
        name="dynamic_preferences.user"),
    url(r'^user/(?P<section>\w+)$', 
        login_required(views.UserPreferenceFormView.as_view()), 
        name="dynamic_preferences.user.section"),
)

if test:

    urlpatterns += patterns('',
        url(r'^test/template$',views.RegularTemplateView.as_view(), name="dynamic_preferences.test.templateview"),      
    )
