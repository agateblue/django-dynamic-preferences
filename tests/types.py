from dynamic_preferences.types import *

# For testing field instantiation


class TestBooleanPreference(BooleanPreference):
    pass


class TestStringPreference(StringPreference):

    field_attributes = {"initial": "hello world!"}


#
