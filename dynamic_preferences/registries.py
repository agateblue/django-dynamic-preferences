try:
    from django.conf import settings
    from django.db.models.fields import FieldDoesNotExist
    from django.apps import apps
except ImportError:
    pass

try:
    from django.utils.importlib import import_module
except ImportError:
    from importlib import import_module

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


from .managers import PreferencesManager
from .settings import preferences_settings
from .exceptions import NotFoundInRegistry

class PreferenceModelsRegistry(dict):

    """Store relationships beetween preferences model and preferences registry"""

    def register(self, preference_model, preference_registry):
        self[preference_model] = preference_registry
        preference_registry.preference_model = preference_model

        self.attach_manager(preference_model, preference_registry)

    def attach_manager(self, model, registry):
        if not hasattr(model, 'instance'):
            return

        def instance_getter(self):
            return registry.manager(instance=self)

        getter = property(instance_getter)
        instance_class = model._meta.get_field('instance').rel.to
        setattr(instance_class, preferences_settings.MANAGER_ATTRIBUTE, getter)

    def get_by_preference(self, preference):
        return self[preference.__class__]

    def get_by_instance(self, instance):
        """Return a preference registry using a model instance"""
        # we iterate throught registered preference models in order to get the instance class
        # and check if instance is and instance of this class
        for model, registry in self.items():
            try:
                instance_class = model._meta.get_field('instance').rel.to
                if isinstance(instance, instance_class):
                    return registry

            except FieldDoesNotExist:  # global preferences
                pass
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
            self[preference.section.name][preference.name] = preference

        except KeyError:
            self[preference.section.name] = {}
            self[preference.section.name][preference.name] = preference

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
            _section, name = name.split(
                preferences_settings.SECTION_KEY_SEPARATOR)
            return self[_section][name]

        except ValueError:
            pass

        # use standard params
        try:
            return self[section][name]

        except KeyError:
            raise NotFoundInRegistry("No such preference in {0} with section={1} and name={2}".format(
                self.__class__.__name__, section, name))

    def manager(self, **kwargs):
        """Return a preference manager that can be used to retrieve preference values"""
        return PreferencesManager(registry=self, model=self.preference_model, **kwargs)

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


class PerInstancePreferenceRegistry(PreferenceRegistry):
    pass


def clear():
    """
    Remove all data from registries
    """
    from .dynamic_preferences_registry import global_preferences_registry
    global_preferences_registry.clear()
    for model, registry in preference_models.items():
        registry.clear()


def autodiscover(force_reload=False):
    """
    Populate the registry by iterating through every section declared in :py:const:`settings.INSTALLED_APPS`.

    :param force_reload: if set to `True`, the method will reimport previously imported modules, if any
    :type force_reload: bool.
    """
    logger.info('Dynamic-preferences: autodiscovering preferences...')
    if force_reload:
        clear()

    for app in settings.INSTALLED_APPS:
        # try to import self.package inside current app
        package = '{0}.{1}'.format(
            app, preferences_settings.REGISTRY_MODULE)
        try:
            # print('Dynamic-preferences: importing {0}...'.format(package))
            module = import_module(package)

            if force_reload:
                # mainly used in tests
                reload(module)

        except ImportError as e:
            pass
            # print('Dynamic-preferences: cannnot import {0}, {1}'.format(package, e))
