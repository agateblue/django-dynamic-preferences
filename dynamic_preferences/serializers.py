from __future__ import unicode_literals
import decimal
from six import string_types
from django.utils import six

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

class BooleanSerializer(BaseSerializer):

    true = (
        "True",
        "true",
        "TRUE",
        "1",
        "YES",
        "Yes"
        "yes",
    )

    false = (
        "False",
        "false",
        "FALSE",
        "0",
        "No",
        "no"
        "NO"
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
            raise cls.exception("Value {0} cannot be converted to int")

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
            if value == UNSET:
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
