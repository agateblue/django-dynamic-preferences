try:
    from django.urls import include, re_path
except ImportError:
    from django.conf.urls import include, url as re_path

from django.contrib.admin.views.decorators import staff_member_required
from . import views
from .registries import global_preferences_registry
from .forms import GlobalPreferenceForm

app_name = "dynamic_preferences"

urlpatterns = [
    re_path(
        r"^global/$",
        staff_member_required(
            views.PreferenceFormView.as_view(
                registry=global_preferences_registry, form_class=GlobalPreferenceForm
            )
        ),
        name="global",
    ),
    re_path(
        r"^global/(?P<section>[\w\ ]+)$",
        staff_member_required(
            views.PreferenceFormView.as_view(
                registry=global_preferences_registry, form_class=GlobalPreferenceForm
            )
        ),
        name="global.section",
    ),
    re_path(r"^user/", include("dynamic_preferences.users.urls")),
]
