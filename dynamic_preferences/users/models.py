from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from dynamic_preferences.models import PerInstancePreferenceModel


class UserPreferenceModel(PerInstancePreferenceModel):

    instance = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta(PerInstancePreferenceModel.Meta):
        app_label = "dynamic_preferences_users"
        verbose_name = _("user preference")
        verbose_name_plural = _("user preferences")
