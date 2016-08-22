from django.conf.urls import include, url
from dynamic_preferences import views
from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    url(r'^', include("dynamic_preferences.urls")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^test/template$',views.RegularTemplateView.as_view(), name="dynamic_preferences.test.templateview"),      
]