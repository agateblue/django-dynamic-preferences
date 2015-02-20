from django.core.management.base import BaseCommand, CommandError
from dynamic_preferences.models import GlobalPreferenceModel, UserPreferenceModel
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from dynamic_preferences.registries import global_preferences_registry, per_instance_preferences


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
        preferences = global_preferences_registry.preferences()
        for p in preferences:
            p.to_model()

        deleted = delete_preferences(GlobalPreferenceModel.objects.all())
        print("Deleted {0} global preferences".format(len(deleted)))

        for model, preference_class in per_instance_preferences.items():
            deleted = delete_preferences(preference_class.model.objects.all())
            print("Deleted {0} {1} preferences".format(len(deleted), model.__class__.__name__))
            print('Creating missing preferences for {0} model...'.format(model.__class__.__name__))
            for instance in model.objects.all():
                for p in preference_class.registry.preferences():
                    pref = p.to_model(instance=instance)
                    if not pref.pk:
                        pref.save()

