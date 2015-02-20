

from django.conf import settings
from django.utils.importlib import import_module
# import the logging library
import logging

try:
    # use Python3 reload
    from imp import reload

except:

    # we are on Python2
    pass

# Get an instance of a logger
logger = logging.getLogger(__name__)


#: The package where autodiscover will try to find preferences to register
PREFERENCES_PACKAGE = "dynamic_preferences_registry"


class PreferenceModelsRegistry(dict):
    """Store beetween preferences model and preferences registry"""

    def register(self, preference_model, preference_registry):
        self[preference_model] = preference_registry
        preference_registry.preference_model = preference_model

    def get_by_instance(self, instance):
        """Return a preference registry using a model instance"""
        # we iterate throught registered preference models in order to get the instance class
        # and check if instance is and instance of this class
        for model, registry in self.items():
            instance_class = model._meta.get_field('instance').rel.to            
            if isinstance(instance, instance_class):
                return registry
                break

        return None

preference_models = PreferenceModelsRegistry()


class PreferenceRegistry(dict):
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
    preference_model = None

    def register(self, preference_class):
        """
        Store the given preference class in the registry. 

        :param preference_class: a :py:class:`prefs.Preference` subclass
        """
        preference = preference_class(registry=self)
        try:
            self[preference.section][preference.name] = preference

        except KeyError:
            self[preference.section] = {}
            self[preference.section][preference.name] = preference

        return preference_class

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


class PerInstancePreferenceRegistry(PreferenceRegistry):
    def create_default_preferences(self, instance):
        """
            Create default preferences models for a given instance
        """
        for preference in self.preferences():
            preference.to_model(instance=instance)
    

def clear():
    """
    Remove all data from registries
    """
    from .dynamic_preferences_registry import global_preferences
    global_preferences.clear()
    for model, registry in preference_models.items():
        registry.clear()

def autodiscover(force_reload=False):
    """
    Populate the registry by iterating through every section declared in :py:const:`settings.INSTALLED_APPS`.

    :param force_reload: if set to `True`, the method will reimport previously imported modules, if any
    :type force_reload: bool.
    """
    print('Dynamic-preferences: autodiscovering preferences...')
    if force_reload:
        clear()


    for app in settings.INSTALLED_APPS:
        # try to import self.package inside current app
        package = '{0}.{1}'.format(app, PREFERENCES_PACKAGE)
        try:
            #print('Dynamic-preferences: importing {0}...'.format(package))
            module = import_module(package)

            if force_reload:
                # mainly used in tests
                reload(module)

        except ImportError as e:
            pass
            #print('Dynamic-preferences: cannnot import {0}, {1}'.format(package, e))
