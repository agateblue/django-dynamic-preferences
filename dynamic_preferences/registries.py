"""
    Preference registries store collections of UserPreference and SitePreference instances
    They do the actual job
"""


class PreferenceRegistry(dict):

    def register(self, app, name, preference):

        try:
            self[app][name] = preference

        except KeyError:
            self[app] = {}
            self[app][name] = preference

    def get(self, app, name, d=None):

        return self[app][name]

user_preferences = PreferenceRegistry()
site_preferences = PreferenceRegistry()