from django.core.management.base import BaseCommand
from dynamic_preferences.exceptions import NotFoundInRegistry
from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.registries import (
    global_preferences_registry,
    preference_models,
)
from dynamic_preferences.settings import preferences_settings


def delete_preferences(queryset):
    """
    Delete preferences objects if they are not present in registry.
    Return a list of deleted objects
    """
    deleted = []

    # Iterate through preferences. If an error is raised when accessing
    # preference object, just delete it
    for p in queryset:
        try:
            p.registry.get(section=p.section, name=p.name, fallback=False)
        except NotFoundInRegistry:
            p.delete()
            deleted.append(p)

    return deleted


class Command(BaseCommand):
    help = (
        "Find and delete preferences from database if they don't exist in "
        "registries. Create preferences that are not present in database"
        "(except when invoked with --skip_create)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip_create",
            action="store_true",
            help="Forces to skip the creation step for missing preferences",
        )

    def handle(self, *args, **options):
        skip_create = options["skip_create"]

        # Create needed preferences
        # Global
        if not skip_create:
            self.stdout.write("Creating missing global preferences...")
            manager = global_preferences_registry.manager()
            manager.all()

        deleted = delete_preferences(GlobalPreferenceModel.objects.all())
        message = "Deleted {deleted} global preferences".format(deleted=len(deleted))
        self.stdout.write(message)

        for preference_model, registry in preference_models.items():
            deleted = delete_preferences(preference_model.objects.all())
            message = "Deleted {deleted} {model} preferences".format(
                deleted=len(deleted),
                model=preference_model.__name__,
            )
            self.stdout.write(message)
            if not hasattr(preference_model, "get_instance_model"):
                continue

            if skip_create:
                continue

            message = "Creating missing preferences for {model} model...".format(
                model=preference_model.get_instance_model().__name__,
            )
            self.stdout.write(message)
            for instance in preference_model.get_instance_model().objects.all():
                getattr(instance, preferences_settings.MANAGER_ATTRIBUTE).all()
