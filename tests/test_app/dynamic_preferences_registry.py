from datetime import timezone
from decimal import Decimal
from dynamic_preferences.types import *
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.users.registries import user_preferences_registry
from dynamic_preferences.preferences import Section
from django.forms import ValidationError
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
    verbose_name = "Maximum user count"
    help_text = "Be careful with this setting"

    def validate(self, value):
        # value can't be equal to 1001, no no no!
        if value == 1001:
            raise ValidationError("Wrong value!")
        return value


class NoDefault(IntPreference):
    section = "user"
    name = "no_default"


class NoModel(ModelChoicePreference):
    section = "blog"
    name = "no_model"
    default = None


@global_preferences_registry.register
class ItemsPerPage(IntPreference):
    section = "user"
    name = "items_per_page"
    default = 25


@global_preferences_registry.register
class FeaturedBlogEntry(ModelChoicePreference):
    section = "blog"
    name = "featured_entry"
    queryset = BlogEntry.objects.all()

    def get_default(self):
        return self.queryset.first()


@global_preferences_registry.register
class BlogLogo(FilePreference):
    section = "blog"
    name = "logo"


@global_preferences_registry.register
class BlogLogo2(FilePreference):
    section = "blog"
    name = "logo2"


@global_preferences_registry.register
class BlogCost(DecimalPreference):
    section = "type"
    name = "cost"
    default = Decimal(0)


@user_preferences_registry.register
class FavoriteVegetable(ChoicePreference):
    choices = (
        ("C", "Carrot"),
        ("T", "Tomato. I know, it's not a vegetable"),
        ("P", "Potato"),
    )
    section = "user"
    name = "favorite_vegetable"
    default = "C"


@user_preferences_registry.register
class FavoriteVegetables(MultipleChoicePreference):
    choices = (
        ("C", "Carrot"),
        ("T", "Tomato. I know, it's not a vegetable"),
        ("P", "Potato"),
    )
    section = "user"
    name = "favorite_vegetables"
    default = ["C", "P"]


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


@global_preferences_registry.register
class ExamDuration(DurationPreference):
    section = "exam"
    name = "duration"
    default = timedelta(hours=3)


@global_preferences_registry.register
class RegistrationDate(DatePreference):
    section = "company"
    name = "RegistrationDate"
    default = date(1998, 9, 4)


@global_preferences_registry.register
class BirthDateTime(DateTimePreference):
    section = Section("child", verbose_name="Child Section Verbose Name")
    name = "BirthDateTime"
    default = datetime(1992, 5, 4, 3, 4, 10, 150, tzinfo=timezone.utc)


@global_preferences_registry.register
class OpenningTime(TimePreference):
    section = "company"
    name = "OpenningTime"
    default = time(hour=8, minute=0)
