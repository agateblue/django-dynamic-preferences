from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

from dynamic_preferences import views
from dynamic_preferences.api.viewsets import GlobalPreferencesViewSet
from dynamic_preferences.users.viewsets import UserPreferencesViewSet

admin.autodiscover()

router = routers.SimpleRouter()
router.register(r'global', GlobalPreferencesViewSet, base_name='global')
router.register(r'user', UserPreferencesViewSet, base_name='user')
# router.register(r'user', AccountViewSet)


urlpatterns = [
    url(r'^', include("dynamic_preferences.urls")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^test/template$',
        views.RegularTemplateView.as_view(),
        name="dynamic_preferences.test.templateview"),
    url(r'^api', include(router.urls, namespace='api'))
]
