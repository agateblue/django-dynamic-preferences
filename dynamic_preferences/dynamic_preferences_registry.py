from .registries import PreferenceRegistry, PerInstancePreferenceRegistry


class GlobalPreferenceRegistry(PreferenceRegistry):
    def populate(self, **kwargs):        
        return self.models(**kwargs)

class UserPreferenceRegistry(PerInstancePreferenceRegistry):
    pass


user_preferences = UserPreferenceRegistry()
global_preferences = GlobalPreferenceRegistry()