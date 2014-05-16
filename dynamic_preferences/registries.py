"""
    Preference registries store collections of Global, User and SitePreference instances
    They do the actual job of registering preferences that are declared via :
    ' preference_instance.register() '
"""

from django.conf import settings
from django.utils.importlib import import_module


class PreferenceRegistry(dict):

    # The package where registry will try to find preferences to register
    package = "preferences"

    name = None

    def register(self, app, name, preference):

        try:
            self[app][name] = preference

        except KeyError:
            self[app] = {}
            self[app][name] = preference

    def get(self, app, name, d=None):

        return self[app][name]

    def apps(self):
        """
            return a list of apps with registered preferences
        """
        return self.keys()



    def preferences(self, app=None):
        """
            Return a list of all registered preferences
            or a list of preferences registered for a given app
        """

        if app is None:
            return [self[app][name] for app in self for name in self[app]]
        else:
            return [self[app][name] for name in self[app]]

    def models(self, app=None, **kwargs):

        return [preference.to_model(**kwargs) for preference in self.preferences(app)]

    def autodiscover(self, force_reload=False):
        """
            Populate the registry by iterating through every app
        """
        self.clear()
        prefix = ""

        try:
            test = settings.DYNAMIC_PREFERENCES_USE_TEST_PREFERENCES
            if test:
                # Import test preferences instead of regular ones
                prefix = ".tests"
        except AttributeError, e:
            pass

        for app in settings.INSTALLED_APPS:
            # try to import self.package inside current app
            package = '{0}{1}.{2}'.format(app, prefix, self.package)
            try:
                mod = import_module(package)
                if force_reload:
                    # mainly used in tests
                    reload(mod)

            except ImportError:
                # Module does not exist
                pass

        print("autodiscovered:", self)
        return self

user_preferences = PreferenceRegistry()
site_preferences = PreferenceRegistry()
global_preferences = PreferenceRegistry()