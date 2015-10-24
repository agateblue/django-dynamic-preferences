from dynamic_preferences.types import *
from dynamic_preferences import user_preferences_registry, global_preferences_registry
from .models import BlogEntry

# Tutorial preferences

@global_preferences_registry.register
class RegistrationAllowed(BooleanPreference):
    """
    Are new registrations allowed ?
    """
    section = "user"
    name = "registration_allowed"
    default = False

@global_preferences_registry.register
class MaxUsers(IntPreference):
    """
    Are new registrations allowed ?
    """
    section = "user"
    name = "max_users"
    default = 100


@global_preferences_registry.register
class FeaturedBlogEntry(ModelChoicePreference):
    section = "blog"
    name = "featured_entry"
    queryset = BlogEntry.objects.all()

    def get_default(self):
        return self.queryset.first()

class NoDefault(IntPreference):
    section = "user"
    name = "no_default"

@global_preferences_registry.register
class ItemsPerPage(IntPreference):

    section = "user"
    name = "items_per_page"
    default = 25

@user_preferences_registry.register
class FavoriteVegetable(ChoicePreference):

    choices = (
        ("C", "Carrot"),
        ("T", "Tomato. I know, it's not a vegetable"),
        ("P", "Potato")
    )
    section = "user"
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

class BaseTestPref(object):
    section = "test"


# No section pref
@global_preferences_registry.register
class NoSection(BooleanPreference):
    name = "no_section"
    default = False



# User preferences
@user_preferences_registry.register
class TestUserPref1(BaseTestPref, StringPreference):
    name = "TestUserPref1"
    default = "default value"

@user_preferences_registry.register
class TestUserPref2(BaseTestPref, StringPreference):
    name = "TestUserPref2"
    default = "default value"

@user_preferences_registry.register
class UserBooleanPref(BaseTestPref, BooleanPreference):
    name = "SiteBooleanPref"
    default = False

@user_preferences_registry.register
class UserStringPref(BaseTestPref, StringPreference):
    name = "SUserStringPref"
    default = "Hello world!"

# Global
@global_preferences_registry.register
class TestGlobal1(BaseTestPref, StringPreference):
    name = "TestGlobal1"
    default = "default value"


@global_preferences_registry.register
class TestGlobal2(BaseTestPref, BooleanPreference):
    name = "TestGlobal2"
    default = False


@global_preferences_registry.register
class TestGlobal3(BaseTestPref, BooleanPreference):
    name = "TestGlobal3"
    default = False
