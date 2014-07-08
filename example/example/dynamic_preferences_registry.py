from dynamic_preferences.preferences import UserPreference, SitePreference, GlobalPreference
from dynamic_preferences.types import *
from dynamic_preferences.registries import register



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

