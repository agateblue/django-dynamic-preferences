from django.dispatch import Signal

# Arguments provided to listeners: "section", "name", "old_value" and "new_value"
preference_updated = Signal()
