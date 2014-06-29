"""
    Class defined here are used by dynamic_preferences.preferences to specify
    preferences types (Bool, int, etc.) and rules according validation

"""
from django.forms import CharField, IntegerField, BooleanField, ChoiceField
from dynamic_preferences.serializers import *


class BasePreferenceType(object):

    # A form field that will be used to display and edit the preference
    # use a class, not an instance
    field = None

    # these default will merged with ones from field_attributes
    # then pass to class provided in field in order to instantiate the actual field

    _default_field_attributes = {
        "required": True,
    }

    # Override this attribute to change field behaviour
    field_attributes = {}

    # A serializer class (see dynamic_preferences.serializers)
    serializer = None

    def __init__(self):
        name = self.__class__.__name__
        if name == "FavoriteColour":
            pass
            #print(name, self.__class__.__bases__, self._default_field_attributes)
        self.setup_field()

    def setup_field(self):
        """
            Create an actual instance of self.field
            Override this method if needed
        """
        self._default_field_attributes.update(self.field_attributes)

        self.field = self.field(**self._default_field_attributes)


class BooleanPreference(BasePreferenceType):

    _default_field_attributes = {
        "required": False,  # Hack because of django boolean field handling
    }

    field = BooleanField
    serializer = BooleanSerializer


class IntPreference(BasePreferenceType):

    field = IntegerField
    serializer = IntSerializer


class StringPreference(BasePreferenceType):

    field = CharField
    serializer = StringSerializer


class ChoicePreference(BasePreferenceType):

    field = ChoiceField


