from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [

    url(r'^$',
        login_required(views.UserPreferenceFormView.as_view()),
        name="user"),
    url(r'^(?P<section>[\w\ ]+)$',
        login_required(views.UserPreferenceFormView.as_view()),
        name="user.section"),
]
