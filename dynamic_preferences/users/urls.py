try:
    from django.urls import include, re_path
except ImportError:
    from django.conf.urls import include, url as re_path

from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    re_path(r"^$", login_required(views.UserPreferenceFormView.as_view()), name="user"),
    re_path(
        r"^(?P<section>[\w\ ]+)$",
        login_required(views.UserPreferenceFormView.as_view()),
        name="user.section",
    ),
]
