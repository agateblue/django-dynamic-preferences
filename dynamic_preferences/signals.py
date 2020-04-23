from django.dispatch import Signal

preference_updated = Signal(providing_args=("section", "name", "old_value", "new_value"))
