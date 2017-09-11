from django.core.management.base import BaseCommand, CommandError
from dynamic_preferences.exceptions import NotFoundInRegistry
from dynamic_preferences.models import GlobalPreferenceModel
from dynamic_preferences.registries import preference_models, global_preferences_registry

import logging
logger = logging.getLogger(__name__)


def delete_preferences(queryset):
    """
    Delete preferences objects if they are not present in registry. Return a list of deleted objects
    """
    deleted = []

    # Iterate through preferences. If an error is raised when accessing preference object, just delete it
    for p in queryset:
        try:
            pref = p.registry.get(section=p.section, name=p.name, fallback=False)
        except NotFoundInRegistry:
            p.delete()
            deleted.append(p)

    return deleted


class Command(BaseCommand):
    help = "Find and delete preferences from database if they don't exist in registries. Create preferences that are " \
           "not present in database"

    def handle(self, *args, **options):

        # Create needed preferences
        # Global
        logger.info('Creating missing global preferences...')
        manager = global_preferences_registry.manager()
        manager.all()

        deleted = delete_preferences(GlobalPreferenceModel.objects.all())
        logger.info("Deleted {0} global preferences".format(len(deleted)))

        for preference_model, registry in preference_models.items():
            deleted = delete_preferences(preference_model.objects.all())
            logger.info("Deleted {0} {1} preferences".format(len(deleted), preference_model.__name__))
            if not hasattr(preference_model, 'get_instance_model'):
                continue

            logger.info('Creating missing preferences for {0} model...'.format(preference_model.get_instance_model().__name__))
            for instance in preference_model.get_instance_model().objects.all():
                instance.preferences.all()
