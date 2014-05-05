from registries import user_preferences, site_preferences


class BasePref:

    # The registry in which settings are stored
    registry = None

    name = ""
    value = None
    default = None

    def register(self):
        self.registry[self.name] = self


class UserPreference(BasePref):
    registry = user_preferences


class SitePreference(BasePref):
    registry = site_preferences