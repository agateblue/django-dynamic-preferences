from django.core.management.base import BaseCommand, CommandError
from dynamic_preferences.models import GlobalPreferenceModel, UserPreferenceModel, SitePreferenceModel

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
    help = "Find and delete preferences from database if they don't exist in registries"

    def handle(self, *args, **options):

        deleted = delete_preferences(GlobalPreferenceModel.objects.all())
        print("Deleted {0} global preference models : {1}".format(
            len(deleted),
            ", ".join(['Section: {0} - Name: {1}'.format(p.section, p.name) for p in deleted])
            )
        )

        deleted = delete_preferences(UserPreferenceModel.objects.all())
        print("Deleted {0} user preference models : {1}".format(
            len(deleted),
            ", ".join(['Section: {0} - Name: {1}'.format(p.section, p.name) for p in deleted])
            )
        )

        deleted = delete_preferences(SitePreferenceModel.objects.all())
        print("Deleted {0} site preference models : {1}".format(
            len(deleted),
            ", ".join(['Section: {0} - Name: {1}'.format(p.section, p.name) for p in deleted])
            )
        )


