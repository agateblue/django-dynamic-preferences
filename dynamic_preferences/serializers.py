from __future__ import unicode_literals
import decimal
import os

from datetime import date, timedelta, datetime

from django.conf import settings
from django.utils.dateparse import parse_duration, parse_datetime, parse_date
from django.utils.duration import duration_string
from django.utils.encoding import force_text
from django.utils.timezone import utc, is_aware, make_aware, make_naive, get_default_timezone
from six import string_types
from django.utils import six
from django.db.models.fields.files import FieldFile


class UnsetValue(object):
    pass
UNSET = UnsetValue()

class SerializationError(Exception):
    pass

class BaseSerializer:
    """
        A serializer take a Python variable and returns a string that can be stored safely in database
    """
    exception = SerializationError

    @classmethod
    def serialize(cls, value, **kwargs):
        """
        Return a string from a Python var
        """
        return cls.to_db(value, **kwargs)

    @classmethod
    def deserialize(cls, value, **kwargs):
        """
            Convert a python string to a var
        """
        return cls.to_python(value, **kwargs)

    @classmethod
    def to_python(cls, value, **kwargs):
        raise NotImplementedError

    @classmethod
    def to_db(cls, value, **kwargs):
        return six.text_type(cls.clean_to_db_value(value))

    @classmethod
    def clean_to_db_value(cls, value):
        return value


class InstanciatedSerializer(BaseSerializer):
    """
    In some situations, such as with FileSerializer,
    we need the serializer to be an instance and not a class
    """

    def serialize(self, value, **kwargs):
        return self.to_db(value, **kwargs)

    def deserialize(self, value, **kwargs):
        return self.to_python(value, **kwargs)

    def to_python(self, value, **kwargs):
        raise NotImplementedError

    def to_db(self, value, **kwargs):
        return six.text_type(self.clean_to_db_value(value))

    def clean_to_db_value(self, value):
        return value


class BooleanSerializer(BaseSerializer):

    true = (
        "True",
        "true",
        "TRUE",
        "1",
        "YES",
        "Yes",
        "yes",
    )

    false = (
        "False",
        "false",
        "FALSE",
        "0",
        "No",
        "no",
        "NO",
    )


    @classmethod
    def clean_to_db_value(cls, value):
        if not isinstance(value, bool):
            raise cls.exception('{0} is not a boolean'.format(value))
        return value

    @classmethod
    def to_python(cls, value, **kwargs):

        if value in cls.true:
            return True

        elif value in cls.false:
            return False

        else:
            raise cls.exception("Value {0} can't be deserialized to a Boolean".format(value))


class IntegerSerializer(BaseSerializer):

    @classmethod
    def clean_to_db_value(cls, value):
        if not isinstance(value, int):
            raise cls.exception('IntSerializer can only serialize int values')
        return value

    @classmethod
    def to_python(cls, value, **kwargs):
        try:
            return int(value)
        except:
            raise cls.exception("Value {0} cannot be converted to int".format(value))

IntSerializer = IntegerSerializer

class DecimalSerializer(BaseSerializer):

    @classmethod
    def clean_to_db_value(cls, value):
        if not isinstance(value, decimal.Decimal):
            raise cls.exception('DecimalSerializer can only serialize Decimal instances')
        return value

    @classmethod
    def to_python(cls, value, **kwargs):
        try:
            return decimal.Decimal(value)
        except decimal.InvalidOperation:
            raise cls.exception("Value {0} cannot be converted to decimal".format(value))


class FloatSerializer(BaseSerializer):

    @classmethod
    def clean_to_db_value(cls, value):
        if not isinstance(value, float):
            raise cls.exception('FloatSerializer can only serialize Float instances')
        return value

    @classmethod
    def to_python(cls, value, **kwargs):
        try:
            return float(value)
        except float.InvalidOperation:
            raise cls.exception("Value {0} cannot be converted to float".format(value))

from django.template import defaultfilters

class StringSerializer(BaseSerializer):

    @classmethod
    def to_db(cls, value, **kwargs):
        if not isinstance(value, string_types):
            raise cls.exception("Cannot serialize, value {0} is not a string".format(value))

        if kwargs.get("escape_html", False):
            return defaultfilters.force_escape(value)
        else:
            return value

    @classmethod
    def to_python(cls, value, **kwargs):
        """String deserialisation just return the value as a string"""
        if not value:
            return ''
        try:
            return str(value)
        except: pass
        try:
            return value.encode('utf-8')
        except: pass
        raise cls.exception("Cannot deserialize value {0} tostring".format(value))


def ModelSerializer(model):

    class S(BaseSerializer):
        @classmethod
        def to_db(cls, value, **kwargs):
            if not value or (value == UNSET):
                return None
            return str(value.pk)

        @classmethod
        def to_python(cls, value, **kwargs):
            if value is None:
                return
            try:
                pk = int(value)
            except:
                raise cls.exception("Value {0} cannot be converted to pk".format(value))
            return model.objects.get(pk=value)
    return S


class PreferenceFieldFile(FieldFile):
    """
    In order to have the same API that we have with models.FileField,
    we must return a FieldFile object. However, there are various
    things we have to override, since our files are not bound to a model
    field.
    """

    def __init__(self, preference, storage, name):
        super(FieldFile, self).__init__(None, name)

        # FieldFile also needs a model instance to save changes.
        class FakeInstance(object):
            """
            FieldFile needs a model instance to update when file is persisted
            or deleted
            """
            def save(self):
                return

        self.instance = FakeInstance()

        class FakeField(object):
            """
            FieldFile needs a field object to generate a filename, persist
            and delete files, so we are effectively mocking that.
            """
            name = 'noop'
            max_length = 10000

            def generate_filename(field, instance, name):
                return os.path.join(
                    self.preference.get_upload_path(),
                    f.name)
        self.field = FakeField()
        self.storage = storage
        self._committed = True
        self.preference = preference


class FileSerializer(InstanciatedSerializer):
    """
    Since this serializer requires additional data from the preference
    especially the upload path, we cannot do it without binding it
    to the preference

    it is therefore designed to be explicitely instanciated by the preference
    object.
    """
    def __init__(self, preference):
        self.preference = preference

    def to_db(self, f, **kwargs):
        if not f:
            return
        path = os.path.join(
            self.preference.get_upload_path(),
            f.name)
        saved_path = self.preference.get_file_storage().save(path, f)

        return saved_path

    def to_python(self, value, **kwargs):
        if not value:
            return
        storage = self.preference.get_file_storage()

        return PreferenceFieldFile(
            preference=self.preference,
            storage=storage,
            name=value)


class DurationSerializer(BaseSerializer):
    @classmethod
    def to_db(cls, value, **kwargs):
        if not isinstance(value, timedelta):
            raise cls.exception("Cannot serialize, value {0} is not a timedelta".format(value))

        return duration_string(value)

    @classmethod
    def to_python(cls, value, **kwargs):
        parsed = parse_duration(force_text(value))
        if parsed is None:
            raise cls.exception("Value {0} cannot be converted to timedelta".format(value))
        return parsed


class DateSerializer(BaseSerializer):
    @classmethod
    def to_db(cls, value, **kwargs):
        if not isinstance(value, date):
            raise cls.exception("Cannot serialize, value {0} is not a date object".format(value))

        return value.isoformat()

    @classmethod
    def to_python(cls, value, **kwargs):
        parsed = parse_date(force_text(value))
        if parsed is None:
            raise cls.exception("Value {0} cannot be converted to a date object".format(value))

        return parsed


class DateTimeSerializer(BaseSerializer):
    @classmethod
    def to_db(cls, value, **kwargs):
        if not isinstance(value, datetime):
            raise cls.exception("Cannot serialize, value {0} is not a datetime object".format(value))

        value = cls.enforce_timezone(value)

        return value.isoformat()

    @classmethod
    def enforce_timezone(cls, value):
        """
        When `self.default_timezone` is `None`, always return naive datetimes.
        When `self.default_timezone` is not `None`, always return aware datetimes.
        """
        field_timezone = cls.default_timezone()

        if (field_timezone is not None) and not is_aware(value):
            return make_aware(value, field_timezone)
        elif (field_timezone is None) and is_aware(value):
            return make_naive(value, utc)
        return value

    @classmethod
    def default_timezone(cls):
        return get_default_timezone() if settings.USE_TZ else None

    @classmethod
    def to_python(cls, value, **kwargs):
        parsed = parse_datetime(force_text(value))
        if parsed is None:
            raise cls.exception("Value {0} cannot be converted to a datetime object".format(value))
        return parsed
