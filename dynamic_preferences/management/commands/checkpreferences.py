from django.core.management.base import BaseCommand, CommandError
from dynamic_preferences.models import GlobalPreferenceModel, UserPreferenceModel
from dynamic_preferences import global_preferences
from dynamic_preferences.registries import preference_models


def delete_preferences(queryset):
    """
    Delete preferences objects if they are not present in registry. Return a list of deleted objects
    """
    deleted = []

    # Iterate through preferences. If an error is raised when accessing preference object, just delete it
    for p in queryset:
        try:
            pref = p.preference
        except KeyError:
            p.delete()
            deleted.append(p)

    return deleted


class Command(BaseCommand):
    help = "Find and delete preferences from database if they don't exist in registries. Create preferences that are " \
           "not present in database"

    def handle(self, *args, **options):

        # Create needed preferences
        # Global
        print('Creating missing global preferences...')        
        preferences = global_preferences.preferences()
        for p in preferences:
            p.to_model()

        deleted = delete_preferences(GlobalPreferenceModel.objects.all())
        print("Deleted {0} global preferences".format(len(deleted)))

        for preference_model, registry in preference_models.items():
            deleted = delete_preferences(preference_model.objects.all())
            print("Deleted {0} {1} preferences".format(len(deleted), preference_model.__class__.__name__))
            print('Creating missing preferences for {0} model...'.format(preference_model.get_instance_model().__name__))
            for instance in preference_model.get_instance_model().objects.all():
                for p in registry.preferences():
                    pref = p.to_model(instance=instance)
                    if not pref.pk:
                        pref.save()

