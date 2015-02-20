from .registries import PreferenceRegistry, PerInstancePreferenceRegistry


class GlobalPreferenceRegistry(PreferenceRegistry):
    def populate(self, **kwargs):        
        return self.models(**kwargs)

class UserPreferenceRegistry(PerInstancePreferenceRegistry):
    pass


user_preference_registry = UserPreferenceRegistry()
global_preference_registry = GlobalPreferenceRegistry()