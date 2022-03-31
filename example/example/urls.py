try:
    from django.urls import include, re_path
except ImportError:
    from django.conf.urls import include, url as re_path

from django.contrib import admin

admin.autodiscover()


urlpatterns = [
    # Examples:
    # re_path(r'^$', 'example.views.home', name='home'),
    # re_path(r'^blog/', include('blog.urls')),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^preferences/", include("dynamic_preferences.urls")),
]
