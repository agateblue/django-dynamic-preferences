from dynamic_preferences.types import *
# For testing field instantiation


class TestBooleanPreference(BooleanPreference):
    pass


class TestOverrideBooleanPreference(BooleanPreference):
    field_attributes = {
        "required": True,
        "initial": True
    }



class TestStringPreference(StringPreference):

    field_attributes = {
        "initial": "hello world!"
    }

