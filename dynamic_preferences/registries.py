

from django.conf import settings
from django.utils.importlib import import_module
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class PreferencesRegistry(dict):
    """
    Registries are special dictionaries that are used by dynamic-preferences to register and access your preferences.
    dynamic-preferences has one registry per Preference type:

    - :py:const:`user_preferences`
    - :py:const:`site_preferences`
    - :py:const:`global_preferences`

    In order to register preferences automatically, you must call :py:func:`autodiscover` in your URLconf.

    """

    #: a name to identify the registry
    name = "preferences_registry"
    def register(self, name, section, preference):
        """
        Store the given preference in the registry. Will also create the preference in database if it does not exist

        This method is called by :py:class:`prefs.BasePreference`.
        You should not have to call it manually.

        :param section: The section name under which the preference should be registered
        :type section: str.
        :param name: The name of the preference
        :type name: str.
        :param preference: a :py:class:`prefs.BasePreference` instance
        """
        try:
            self[section][name] = preference

        except KeyError:
            self[section] = {}
            self[section][name] = preference

    def get(self, name, section=None):
        """
        Returns a previously registered preference

        :param section: The section name under which the preference is registered
        :type section: str.
        :param name: The name of the preference. You can use dotted notation 'section.name' if you want to avoid providing section param
        :type name: str.
        :return: a :py:class:`prefs.BasePreference` instance
        """
        # try dotted notation
        try:
            section, name = name.split('.')
            return self[section][name]
            
        except ValueError:
            pass

        # use standard params
        try:
            return self[section][name]

        except:    
            raise KeyError("No such preference in {0} with section={1} and name={2}".format(
                self.__class__.__name__, section, name))

    def sections(self):
        """
        :return: a list of apps with registered preferences
        :rtype: list
        """

        return self.keys()

    def preferences(self, section=None):
        """
        Return a list of all registered preferences
        or a list of preferences registered for a given section

        :param section: The section name under which the preference is registered
        :type section: str.
        :return: a list of :py:class:`prefs.BasePreference` instances
        """

        if section is None:
            return [self[section][name] for section in self for name in self[section]]
        else:
            return [self[section][name] for name in self[section]]

    def models(self, section=None, **kwargs):
        """
        Return a list of model instances corresponding to registered preferences
        This method calls :py:meth:`preferences.BasePreference.to_model`, see related documentation for more information

        :param section: The section name under which the preferences are registered
        :type section: str.
        :param kwargs: Keyword arguments that will be passed directly to `to_model()`
        :return: a list of :py:class:`models.BasePreferenceModel` instances
        """

        return [preference.to_model(**kwargs) for preference in self.preferences(section)]

    def populate(self, **kwargs):
        """
        Populate database with registered preferences and default values
        """
        raise NotImplementedError

#: The package where autodiscover will try to find preferences to register
preferences_package = "dynamic_preferences_registry"

class GlobalPreferencesRegistry(PreferencesRegistry):
    def populate(self, **kwargs):
        
        return self.models(**kwargs)

class SitePreferencesRegistry(PreferencesRegistry):
    pass

class UserPreferencesRegistry(PreferencesRegistry):
    
    def create_default_preferences(self, user):
        """
            Create default preferences models for a given user
        """
        for preference in self.preferences():
            preference.to_model(user=user)

user_preferences_registry = UserPreferencesRegistry()
site_preferences_registry = SitePreferencesRegistry()
global_preferences_registry = GlobalPreferencesRegistry()

def clear():
    """
    Remove all data from registries
    """
    global_preferences_registry.clear()
    site_preferences_registry.clear()
    user_preferences_registry.clear()

def autodiscover(force_reload=True):
    """
    Populate the registry by iterating through every section declared in :py:const:`settings.INSTALLED_APPS`.

    :param force_reload: if set to `True`, the method will reimport previously imported modules, if any
    :type force_reload: bool.
    """
    print('Dynamic-preferences: autodiscovering preferences...')
    clear()
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
        package = '{0}{1}.{2}'.format(app, prefix, preferences_package)

        try:
            #print('Dynamic-preferences: importing {0}...'.format(package))
            mod = import_module(package)
            if force_reload:
                # mainly used in tests
                reload(mod)

        except ImportError, e:
            pass
            #print('Dynamic-preferences: cannnot import {0}, {1}'.format(package, e))

    global_preferences_registry.populate()

def register(cls):
    instance = cls()

    cls.registry.register(name=cls.name, section=cls.section, preference=instance)
    
    return cls