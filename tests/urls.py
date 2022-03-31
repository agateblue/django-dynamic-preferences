try:
    from django.urls import include, re_path
except ImportError:
    from django.conf.urls import include, url as re_path

from django.contrib import admin
from rest_framework import routers

from dynamic_preferences import views
from dynamic_preferences.api.viewsets import GlobalPreferencesViewSet
from dynamic_preferences.users.viewsets import UserPreferencesViewSet

admin.autodiscover()

router = routers.SimpleRouter()
router.register(r"global", GlobalPreferencesViewSet, "global")
router.register(r"user", UserPreferencesViewSet, "user")
# router.register(r'user', AccountViewSet)


urlpatterns = [
    re_path(r"^", include("dynamic_preferences.urls")),
    re_path(r"^admin/", admin.site.urls),
    re_path(
        r"^test/template$",
        views.RegularTemplateView.as_view(),
        name="dynamic_preferences.test.templateview",
    ),
    re_path(r"^api", include((router.urls, "api"), namespace="api")),
]
