from dynamic_preferences.preferences import UserPreference, SitePreference, GlobalPreference
from dynamic_preferences.types import *
from dynamic_preferences.registries import register


# Tutorial preferences

@register
class RegistrationAllowed(BooleanPreference, GlobalPreference):
    """
    Are new registrations allowed ?
    """
    section = "user"
    name = "registration_allowed"
    default = False

@register
class MaxUsers(IntPreference, GlobalPreference):
    """
    Are new registrations allowed ?
    """
    section = "user"
    name = "max_users"
    default = 100

@register
class ItemsPerPage(IntPreference, GlobalPreference):
   
    section = "user"
    name = "items_per_page"
    default = 25

@register
class FavoriteVegetable(ChoicePreference, GlobalPreference):

    choices = (
        ("C", "Carrot"),
        ("T", "Tomato. I know, it's not a vegetable"),
        ("P", "Potato")
    )
    section = "user"
    name = "favorite_vegetable"
    default = "C"

@register
class FavouriteColour(UserPreference, StringPreference):
    """
    What's your favourite colour ?
    """
    section = "misc"
    name = "favourite_colour"
    default = "Green"

@register
class IsZombie(BooleanPreference, UserPreference):
    """
    Are you a zombie ?
    """
    section = "misc"
    name = "is_zombie"
    default = True

class BaseTestPref(object):
    section = "test"


# No section pref
@register
class NoSection(BooleanPreference, GlobalPreference):
    name = "no_section"
    default = False



# User preferences
@register
class TestUserPref1(StringPreference, BaseTestPref, UserPreference):
    name = "TestUserPref1"
    default = "default value"

@register
class TestUserPref2(StringPreference, BaseTestPref, UserPreference):
    name = "TestUserPref2"

@register
class UserBooleanPref(BooleanPreference, BaseTestPref, UserPreference):
    name = "SiteBooleanPref"
    default = False

@register
class UserStringPref(StringPreference, BaseTestPref, UserPreference):
    name = "SUserStringPref"
    default = "Hello world!"


# Site Preferences
@register
class TestSitePref1(StringPreference, BaseTestPref, SitePreference):
    name = "TestSitePref1"
    default = "site default value"

@register
class TestSitePref2(StringPreference, BaseTestPref, SitePreference):
    name = "TestSitePref2"

@register
class SiteBooleanPref(BooleanPreference, BaseTestPref, SitePreference):
    name = "SiteBooleanPref"
    default = False

@register
class SiteIntPref(IntPreference, BaseTestPref, SitePreference):
    name = "SiteIntPref"
    default = 2

# Global
@register
class TestGlobal1(StringPreference, BaseTestPref, GlobalPreference):
    name = "TestGlobal1"
    default = "default value"


@register
class TestGlobal2(BooleanPreference, BaseTestPref, GlobalPreference):
    name = "TestGlobal2"
    default = False


@register
class TestGlobal3(BooleanPreference, BaseTestPref, GlobalPreference):
    name = "TestGlobal3"
    default = False




