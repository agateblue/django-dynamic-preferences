from ..registries import PerInstancePreferenceRegistry


class UserPreferenceRegistry(PerInstancePreferenceRegistry):
    pass


user_preferences_registry = UserPreferenceRegistry()
