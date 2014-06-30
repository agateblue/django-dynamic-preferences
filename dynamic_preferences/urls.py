from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
admin.autodiscover()


from dynamic_preferences import views
urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^global$', staff_member_required(views.GlobalPreferenceList.as_view()), name="dynamic_preferences.global"),
    url(r'^global/(?P<app>\w+)$', views.GlobalAppPreferenceList.as_view(), name="dynamic_preferences.global.list.app"),


) + staticfiles_urlpatterns()

from dynamic_preferences.registries import autodiscover
autodiscover()