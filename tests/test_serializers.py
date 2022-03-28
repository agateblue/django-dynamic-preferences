import pytest

from datetime import timezone
from decimal import Decimal

from datetime import date, timedelta, datetime, time
from django.test import TestCase, override_settings
from django.template import defaultfilters

from dynamic_preferences import serializers
from .test_app.models import BlogEntry, BlogEntryWithNonIntPk


@pytest.fixture
def blog_entries(db):
    BlogEntry.objects.bulk_create(
        [
            BlogEntry(title="This is a test", content="Hello World"),
            BlogEntry(title="This is only a test", content="Hello World"),
        ]
    )
    BlogEntryWithNonIntPk.objects.bulk_create(
        [
            BlogEntryWithNonIntPk(title="This is a test", content="Hello World"),
            BlogEntryWithNonIntPk(title="This is only a test", content="Hello World"),
        ]
    )


def test_boolean_serialization():
    s = serializers.BooleanSerializer

    assert s.serialize(True) == "True"
    assert s.serialize(False) == "False"
    with pytest.raises(s.exception):
        s.serialize("yolo")


def test_boolean_deserialization():

    s = serializers.BooleanSerializer

    for v in s.true:
        assert s.deserialize(v) == True

    for v in s.false:
        assert s.deserialize(v) == False

    with pytest.raises(s.exception):
        s.deserialize("I'm a true value")


def test_int_serialization():

    s = serializers.IntSerializer

    assert s.serialize(1) == "1"
    assert s.serialize(666) == "666"
    assert s.serialize(-144) == "-144"
    assert s.serialize(0) == "0"
    assert s.serialize(123456) == "123456"

    with pytest.raises(s.exception):
        s.serialize("I'm an integer")


def test_decimal_serialization():

    s = serializers.DecimalSerializer

    assert s.serialize(Decimal("1")) == "1"
    assert s.serialize(Decimal("-1")) == "-1"
    assert s.serialize(Decimal("-666.6")) == "-666.6"
    assert s.serialize(Decimal("666.6")) == "666.6"

    with pytest.raises(s.exception):
        s.serialize("I'm a decimal")


def test_float_serialization():

    s = serializers.FloatSerializer

    assert s.serialize(1.0) == "1.0"
    assert s.serialize(-1.0) == "-1.0"
    assert s.serialize(1) == "1.0"
    assert s.serialize(-1) == "-1.0"
    assert s.serialize(-666.6) == "-666.6"
    assert s.serialize(666.6) == "666.6"

    with pytest.raises(s.exception):
        s.serialize("I'm a float")


def test_float_deserialization():

    s = serializers.FloatSerializer

    assert s.deserialize("1.0") == float("1.0")
    assert s.deserialize("-1.0") == float("-1.0")
    assert s.deserialize("-666.6") == float("-666.6")
    assert s.deserialize("666.6") == float("666.6")

    with pytest.raises(s.exception):
        s.serialize("I'm a float")


def test_int_deserialization():

    s = serializers.DecimalSerializer

    assert s.deserialize("1") == Decimal("1")
    assert s.deserialize("-1") == Decimal("-1")
    assert s.deserialize("-666.6") == Decimal("-666.6")
    assert s.deserialize("666.6") == Decimal("666.6")

    with pytest.raises(s.exception):
        s.serialize("I'm a decimal!")


def test_string_serialization():

    s = serializers.StringSerializer

    assert s.serialize("Bonjour") == "Bonjour"
    assert s.serialize("12") == "12"
    assert (
        s.serialize("I'm a long sentence, but I rock")
        == "I'm a long sentence, but I rock"
    )

    # check for HTML escaping
    kwargs = {
        "escape_html": True,
    }
    assert s.serialize(
        "<span>Please, I don't wanna disappear</span>", **kwargs
    ) == defaultfilters.force_escape("<span>Please, I don't wanna disappear</span>")

    with pytest.raises(s.exception):
        s.serialize(("I", "Want", "To", "Be", "A", "String"))


def test_string_deserialization():

    s = serializers.StringSerializer
    assert s.deserialize("Bonjour") == "Bonjour"
    assert s.deserialize("12") == "12"
    assert (
        s.deserialize("I'm a long sentence, but I rock")
        == "I'm a long sentence, but I rock"
    )

    # check case where empty string (value can be None)
    assert s.deserialize(None) == ""
    assert s.deserialize("") == ""

    kwargs = {
        "escape_html": True,
    }
    assert s.deserialize(
        s.serialize("<span>Please, I don't wanna disappear</span>", **kwargs)
    ) == defaultfilters.force_escape("<span>Please, I don't wanna disappear</span>")


def test_duration_serialization():
    s = serializers.DurationSerializer

    assert s.serialize(timedelta(minutes=1)) == "00:01:00"
    assert s.serialize(timedelta(milliseconds=1)) == "00:00:00.001000"
    assert s.serialize(timedelta(weeks=1)) == "7 00:00:00"

    with pytest.raises(s.exception):
        s.serialize("Not a timedelta")


def test_duration_deserialization():
    s = serializers.DurationSerializer

    assert s.deserialize("7 00:00:00") == timedelta(weeks=1)

    with pytest.raises(s.exception):
        s.deserialize("Invalid duration string")


def test_date_serialization():
    s = serializers.DateSerializer

    assert s.serialize(date(2017, 10, 5)) == "2017-10-05"

    with pytest.raises(s.exception):
        s.serialize("Not a date")


def test_date_deserialization():
    s = serializers.DateSerializer

    assert s.deserialize("1900-01-01") == date(1900, 1, 1)

    with pytest.raises(s.exception):
        s.deserialize("Invalid date string")


def test_datetime_serialization():
    s = serializers.DateTimeSerializer

    # If TZ is enabled default timezone is America/Chicago
    # https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-TIME_ZONE
    assert (
        s.serialize(datetime(2017, 10, 5, 23, 45, 1, 792346))
        == "2017-10-05T23:45:01.792346-05:00"
    )

    with override_settings(USE_TZ=False):
        assert s.serialize(
            datetime(2017, 10, 5, 23, 45, 1, 792346)
        ), "2017-10-05T23:45:01.792346"

    with pytest.raises(s.exception) as ex:
        s.serialize("a string")
        assert ex.exception.args == (
            "Cannot serialize, value 'a string' is not a datetime object",
        )


def test_datetime_deserialization():
    s = serializers.DateTimeSerializer

    assert s.deserialize("2017-10-05T23:45:01.792346") == datetime(
        2017, 10, 5, 23, 45, 1, 792346
    )
    assert s.deserialize("2017-10-05T23:45:01.792346+00:00") == datetime(
        2017, 10, 5, 23, 45, 1, 792346, tzinfo=timezone.utc
    )

    with pytest.raises(s.exception) as ex:
        s.deserialize("abcd")
        assert ex.exception.args == (
            "Value abcd cannot be converted to a datetime object",
        )


def test_time_serialization():
    s = serializers.TimeSerializer

    assert s.serialize(time(hour=5)) == "05:00:00"
    assert s.serialize(time(minute=30)) == "00:30:00"
    assert s.serialize(time(23, 59, 59, 999999)) == "23:59:59.999999"

    with pytest.raises(s.exception):
        s.serialize("Not a time")


def test_time_deserialization():
    s = serializers.TimeSerializer

    assert s.deserialize("23:00:00") == time(hour=23)

    with pytest.raises(s.exception):
        s.deserialize("Invalid time string")


def test_multiple_serialization():
    s = serializers.MultipleSerializer

    assert s.serialize(["a", "b", "c"]) == "a,b,c"
    assert (
        s.serialize(["key,with,comma", "b", "another,key,with,comma"])
        == "another,,key,,with,,comma,b,key,,with,,comma"
    )

    with pytest.raises(s.exception):
        s.serialize(["a", "", "c"])


def test_multiple_deserialization():
    s = serializers.MultipleSerializer

    assert s.deserialize("a,b,c") == ["a", "b", "c"]
    assert s.deserialize("key,,with,,comma,b,another,,key,,with,,comma") == [
        "key,with,comma",
        "b",
        "another,key,with,comma",
    ]


def test_model_multiple_serialization(blog_entries):
    s = serializers.ModelMultipleSerializer(BlogEntry)
    blog_entries = BlogEntry.objects.all()

    assert s.serialize(blog_entries), s.separator.join(
        map(str, sorted(list(blog_entries.values_list("pk", flat=True))))
    )


def test_model_multiple_deserialization(blog_entries):
    s = serializers.ModelMultipleSerializer(BlogEntry)
    blog_entries = BlogEntry.objects.all()
    pks = s.separator.join(
        map(str, sorted(list(blog_entries.values_list("pk", flat=True))))
    )
    assert list(s.deserialize(pks)) == list(blog_entries)


def test_model_multiple_single_serialization(blog_entries):
    s = serializers.ModelMultipleSerializer(BlogEntry)
    blog_entry = BlogEntry.objects.all().first()

    assert s.serialize(blog_entry) == s.separator.join(map(str, [blog_entry.pk]))


def test_model_multiple_serialization_with_non_int_pk(blog_entries):
    s = serializers.ModelMultipleSerializer(BlogEntryWithNonIntPk)
    blog_entries = BlogEntryWithNonIntPk.objects.all()

    assert s.serialize(blog_entries) == s.separator.join(
        map(str, sorted(list(blog_entries.values_list("pk", flat=True))))
    )


def test_model_multiple_deserialization_with_non_int_pk(blog_entries):
    s = serializers.ModelMultipleSerializer(BlogEntryWithNonIntPk)
    blog_entries = BlogEntryWithNonIntPk.objects.all()
    pks = s.separator.join(
        map(str, sorted(list(blog_entries.values_list("pk", flat=True))))
    )

    deserialized_ids = sorted([instance.pk for instance in s.deserialize(pks)])
    blog_entries_ids = sorted([entry.pk for entry in blog_entries])
    assert deserialized_ids, blog_entries_ids


def test_model_multiple_single_serialization_with_non_int_pk(blog_entries):
    s = serializers.ModelMultipleSerializer(BlogEntryWithNonIntPk)
    blog_entry = BlogEntryWithNonIntPk.objects.all().first()

    assert s.serialize(blog_entry) == s.separator.join(map(str, [blog_entry.pk]))
