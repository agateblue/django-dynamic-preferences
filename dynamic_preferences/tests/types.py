from dynamic_preferences.types import *
# For testing field instantiation


class TestBooleanPreference(BooleanPreference):
    pass


class TestOverrideBooleanPreference(BooleanPreference):
    field_attributes = {
        "required": True,
        "initial": True
    }


class TestChoicePreference(StringPreference):

    CHOICES = (
        ("FR", "French"),
        ("EN", "English"),
        ("DE", "Deutsch")
    )

    field_attributes = {
        "initial": "FR",
        "choices": CHOICES
    }


class TestStringPreference(StringPreference):

    field_attributes = {
        "initial": "hello world!"
    }




