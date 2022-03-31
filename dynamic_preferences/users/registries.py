from ..registries import PerInstancePreferenceRegistry


class UserPreferenceRegistry(PerInstancePreferenceRegistry):
    section_url_namespace = "dynamic_preferences:user.section"


user_preferences_registry = UserPreferenceRegistry()
