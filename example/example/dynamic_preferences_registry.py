from dynamic_preferences.types import *
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.users.registries import user_preferences_registry


@global_preferences_registry.register
class RegistrationAllowed(BooleanPreference):
    """
    Are new registrations allowed ?
    """
    verbose_name = 'Allow new users to register'
    section = "auth"
    name = "registration_allowed"
    default = False


@global_preferences_registry.register
class MaxUsers(IntPreference):
    """
    Are new registrations allowed ?
    """
    section = "auth"
    name = "max_users"
    default = 100
    help_text = "Please fill in the form"


@global_preferences_registry.register
class Header(LongStringPreference):

    section = "general"
    name = "presentation"
    default = "You need a presentation"


@user_preferences_registry.register
class ItemsPerPage(IntPreference):

    section = "display"
    name = "items_per_page"
    default = 25


@user_preferences_registry.register
class FavoriteVegetable(ChoicePreference):

    choices = (
        ("C", "Carrot"),
        ("T", "Tomato. I know, it's not a vegetable"),
        ("P", "Potato")
    )
    section = "auth"
    name = "favorite_vegetable"
    default = "C"


@user_preferences_registry.register
class FavouriteColour(StringPreference):
    """
    What's your favourite colour ?
    """
    section = "misc"
    name = "favourite_colour"
    default = "Green"


@user_preferences_registry.register
class IsZombie(BooleanPreference):
    """
    Are you a zombie ?
    """
    section = "misc"
    name = "is_zombie"
    default = True


@user_preferences_registry.register
class IsFanOfTokioHotel(BooleanPreference):

    section = "music"
    name = "is_fan_of_tokio_hotel"
    default = False
