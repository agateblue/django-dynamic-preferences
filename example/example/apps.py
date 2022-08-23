from django.apps import AppConfig
from dynamic_preferences.signals import preference_updated


def notify_on_preference_update(sender, section, name, old_value, new_value, **kwargs):
    print(
        "Preference {} in section {} changed from {} to {}".format(
            name, section, old_value, new_value
        )
    )


class ExampleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "example"

    def ready(self):
        print("Registering signals")
        preference_updated.connect(notify_on_preference_update)
