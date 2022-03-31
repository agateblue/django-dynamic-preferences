import datetime

from decimal import Decimal
from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.users.registries import user_preferences_registry
from dynamic_preferences.preferences import Section
from django.forms import ValidationError
from .models import BlogEntry


# Tutorial preferences
@global_preferences_registry.register
class RegistrationAllowed(types.BooleanPreference):
    """
    Are new registrations allowed ?
    """

    section = "user"
    name = "registration_allowed"
    default = False


@global_preferences_registry.register
class MaxUsers(types.IntPreference):
    """
    Are new registrations allowed ?
    """

    section = "user"
    name = "max_users"
    default = 100
    verbose_name = "Maximum user count"
    help_text = "Be careful with this setting"

    def validate(self, value):
        # value can't be equal to 1001, no no no!
        if value == 1001:
            raise ValidationError("Wrong value!")
        return value


class NoDefault(types.IntPreference):
    section = "user"
    name = "no_default"


class NoModel(types.ModelChoicePreference):
    section = "blog"
    name = "no_model"
    default = None


@global_preferences_registry.register
class ItemsPerPage(types.IntPreference):
    section = "user"
    name = "items_per_page"
    default = 25


@global_preferences_registry.register
class FeaturedBlogEntry(types.ModelChoicePreference):
    section = "blog"
    name = "featured_entry"
    queryset = BlogEntry.objects.all()

    def get_default(self):
        return self.queryset.first()


@global_preferences_registry.register
class BlogLogo(types.FilePreference):
    section = "blog"
    name = "logo"


@global_preferences_registry.register
class BlogLogo2(types.FilePreference):
    section = "blog"
    name = "logo2"


@global_preferences_registry.register
class BlogCost(types.DecimalPreference):
    section = "type"
    name = "cost"
    default = Decimal(0)


@user_preferences_registry.register
class FavoriteVegetable(types.ChoicePreference):
    choices = (
        ("C", "Carrot"),
        ("T", "Tomato. I know, it's not a vegetable"),
        ("P", "Potato"),
    )
    section = "user"
    name = "favorite_vegetable"
    default = "C"


@user_preferences_registry.register
class FavoriteVegetables(types.MultipleChoicePreference):
    choices = (
        ("C", "Carrot"),
        ("T", "Tomato. I know, it's not a vegetable"),
        ("P", "Potato"),
    )
    section = "user"
    name = "favorite_vegetables"
    default = ["C", "P"]


@user_preferences_registry.register
class FavouriteColour(types.StringPreference):
    """
    What's your favourite colour ?
    """

    section = "misc"
    name = "favourite_colour"
    default = "Green"


@user_preferences_registry.register
class IsZombie(types.BooleanPreference):
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
class NoSection(types.BooleanPreference):
    name = "no_section"
    default = False


# User preferences
@user_preferences_registry.register
class TestUserPref1(BaseTestPref, types.StringPreference):
    name = "TestUserPref1"
    default = "default value"


@user_preferences_registry.register
class TestUserPref2(BaseTestPref, types.StringPreference):
    name = "TestUserPref2"
    default = "default value"


@user_preferences_registry.register
class UserBooleanPref(BaseTestPref, types.BooleanPreference):
    name = "SiteBooleanPref"
    default = False


@user_preferences_registry.register
class UserStringPref(BaseTestPref, types.StringPreference):
    name = "SUserStringPref"
    default = "Hello world!"


# Global
@global_preferences_registry.register
class TestGlobal1(BaseTestPref, types.StringPreference):
    name = "TestGlobal1"
    default = "default value"


@global_preferences_registry.register
class TestGlobal2(BaseTestPref, types.BooleanPreference):
    name = "TestGlobal2"
    default = False


@global_preferences_registry.register
class TestGlobal3(BaseTestPref, types.BooleanPreference):
    name = "TestGlobal3"
    default = False


@global_preferences_registry.register
class ExamDuration(types.DurationPreference):
    section = "exam"
    name = "duration"
    default = datetime.timedelta(hours=3)


@global_preferences_registry.register
class RegistrationDate(types.DatePreference):
    section = "company"
    name = "RegistrationDate"
    default = datetime.date(1998, 9, 4)


@global_preferences_registry.register
class BirthDateTime(types.DateTimePreference):
    section = Section("child", verbose_name="Child Section Verbose Name")
    name = "BirthDateTime"
    default = datetime.datetime(1992, 5, 4, 3, 4, 10, 150, tzinfo=datetime.timezone.utc)


@global_preferences_registry.register
class OpenningTime(types.TimePreference):
    section = "company"
    name = "OpenningTime"
    default = datetime.time(hour=8, minute=0)
