from django.db import transaction
from django.db.models import Q

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from dynamic_preferences import models
from dynamic_preferences import exceptions
from dynamic_preferences.settings import preferences_settings

from . import serializers


class PreferenceViewSet(
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    - list preferences
    - detail given preference
    - batch update preferences
    - update a single preference
    """

    def get_queryset(self):
        """
        We just ensure preferences are actually populated before fetching
        from db
        """
        self.init_preferences()
        queryset = super(PreferenceViewSet, self).get_queryset()

        section = self.request.query_params.get("section")
        if section:
            queryset = queryset.filter(section=section)

        return queryset

    def get_manager(self):
        return self.queryset.model.registry.manager()

    def init_preferences(self):
        manager = self.get_manager()
        manager.all()

    def get_object(self):
        """
        Returns the object the view is displaying.
        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        identifier = self.kwargs[lookup_url_kwarg]
        section, name = self.get_section_and_name(identifier)
        filter_kwargs = {"section": section, "name": name}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_section_and_name(self, identifier):
        try:
            section, name = identifier.split(preferences_settings.SECTION_KEY_SEPARATOR)
        except ValueError:
            # no section given
            section, name = None, identifier

        return section, name

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def bulk(self, request, *args, **kwargs):
        """
        Update multiple preferences at once

        this is a long method because we ensure everything is valid
        before actually persisting the changes
        """
        manager = self.get_manager()
        errors = {}
        preferences = []
        payload = request.data

        # first, we check updated preferences actually exists in the registry
        try:
            for identifier, value in payload.items():
                try:
                    preferences.append(self.queryset.model.registry.get(identifier))
                except exceptions.NotFoundInRegistry:
                    errors[identifier] = "invalid preference"
        except (TypeError, AttributeError):
            return Response("invalid payload", status=400)

        if errors:
            return Response(errors, status=400)

        # now, we generate an optimized Q objects to retrieve all matching
        # preferences at once from database
        queries = [Q(section=p.section.name, name=p.name) for p in preferences]

        query = queries[0]
        for q in queries[1:]:
            query |= q
        preferences_qs = self.get_queryset().filter(query)

        # next, we generate a serializer for each database preference
        serializer_objects = []
        for p in preferences_qs:
            s = self.get_serializer_class()(
                p, data={"value": payload[p.preference.identifier()]}
            )
            serializer_objects.append(s)

        validation_errors = {}

        # we check if any serializer is invalid
        for s in serializer_objects:
            if s.is_valid():
                continue
            validation_errors[s.instance.preference.identifier()] = s.errors

        if validation_errors:
            return Response(validation_errors, status=400)

        for s in serializer_objects:
            s.save()

        return Response(
            [s.data for s in serializer_objects],
            status=200,
        )


class GlobalPreferencePermission(permissions.DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.change_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.change_%(model_name)s"],
        "HEAD": ["%(app_label)s.change_%(model_name)s"],
        "POST": ["%(app_label)s.change_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.change_%(model_name)s"],
    }


class GlobalPreferencesViewSet(PreferenceViewSet):
    queryset = models.GlobalPreferenceModel.objects.all()
    serializer_class = serializers.GlobalPreferenceSerializer
    permission_classes = [GlobalPreferencePermission]


class PerInstancePreferenceViewSet(PreferenceViewSet):
    def get_manager(self):
        return self.queryset.model.registry.manager(
            instance=self.get_related_instance()
        )

    def get_queryset(self):
        return (
            super(PerInstancePreferenceViewSet, self)
            .get_queryset()
            .filter(instance=self.get_related_instance())
        )

    def get_related_instance(self):
        """
        Override this to the instance bound to the preferences
        """
        raise NotImplementedError
