from rest_framework import permissions

from dynamic_preferences.api import viewsets

from . import serializers
from . import models


class UserPreferencesViewSet(viewsets.PerInstancePreferenceViewSet):
    queryset = models.UserPreferenceModel.objects.all()
    serializer_class = serializers.UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_related_instance(self):
        return self.request.user
