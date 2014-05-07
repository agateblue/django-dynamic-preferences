"""
    Class defined here are used by dynamic_preferences.preferences to specify
    preferences types (Bool, int, etc.) and rules according validation

"""
from django.forms import CharField, IntegerField, BooleanField
from dynamic_preferences.serializers import *

class BasePreferenceType:

    # A form field that will be used to display and edit the preference
    field = None

    # A serializer class (see dynamic_preferences.serializers)
    serializer = None


class BooleanPreference(BasePreferenceType):

    field = BooleanField(required=False)
    serializer = BooleanSerializer


class IntPreference(BasePreferenceType):

    field = IntegerField()
    serializer = IntSerializer

class StringPreference(BasePreferenceType):

    field = CharField()
    serializer = StringSerializer