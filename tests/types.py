from dynamic_preferences import types

# For testing field instantiation


class TestBooleanPreference(types.BooleanPreference):
    pass


class TestStringPreference(types.StringPreference):

    field_attributes = {"initial": "hello world!"}


#
