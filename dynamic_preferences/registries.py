

from django.conf import settings
from django.utils.importlib import import_module


class PreferenceRegistry(dict):
    """
    Registries are special dictionaries that are used by dynamic-preferences to register and access your preferences.
    dynamic-preferences has one registry per Preference type:

    - :py:const:`user_preferences`
    - :py:const:`site_preferences`
    - :py:const:`global_preferences`

    In order to register preferences automatically, you must call :py:meth:`PreferenceRegistry.autodiscover` on each of these registries in your URLconf.

    """

    #: The package where registry will try to find preferences to register
    package = "dynamic_preferences_registry"

    name = None

    def register(self, app, name, preference):
        """
        Store the given preference in the registry.

        This method is called by :py:class:`prefs.BasePreference`.
        You should not have to call it manually.

        :param app: The app name under which the preference should be registered
        :type app: str.
        :param name: The name of the preference
        :type name: str.
        :param preference: a :py:class:`prefs.BasePreference` instance
        """
        try:
            self[app][name] = preference

        except KeyError:
            self[app] = {}
            self[app][name] = preference

    def get(self, app, name, d=None):
        """
        Returns a previously registered preference

        :param app: The app name under which the preference is registered
        :type app: str.
        :param name: The name of the preference
        :type name: str.
        :param d: The default value that will be returned if parames match no preference
        :return: a :py:class:`prefs.BasePreference` instance
        """
        try:
            return self[app][name]

        except KeyError:
            return d

    def apps(self):
        """
        :return: a list of apps with registered preferences
        :rtype: list
        """

        return self.keys()

    def preferences(self, app=None):
        """
        Return a list of all registered preferences
        or a list of preferences registered for a given app

        :param app: The app name under which the preference is registered
        :type app: str.
        :return: a list of :py:class:`prefs.BasePreference` instances
        """

        if app is None:
            return [self[app][name] for app in self for name in self[app]]
        else:
            return [self[app][name] for name in self[app]]

    def models(self, app=None, **kwargs):
        """
        Return a list of model instances corresponding to registered preferences
        This method calls :py:meth:`preferences.BasePreference.to_model`, see related documentation for more information

        :param app: The app name under which the preference is registered
        :type app: str.
        :param kwargs: Keyword arguments that will be passed directly to `to_model()`
        :return: a list of :py:class:`models.BasePreferenceModel` instances
        """

        return [preference.to_model(**kwargs) for preference in self.preferences(app)]

    def autodiscover(self, force_reload=False):

        """
        Populate the registry by iterating through every app declared in :py:const:`settings.INSTALLED_APPS`.

        :param force_reload: if set to `True`, the method will reimport previously imported modules, if any
        :type force_reload: bool.
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

        return self


user_preferences = PreferenceRegistry()
site_preferences = PreferenceRegistry()
global_preferences = PreferenceRegistry()