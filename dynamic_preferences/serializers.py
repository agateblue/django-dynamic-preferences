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
        raise NotImplementedError

    @classmethod
    def deserialize(cls, value, **kwargs):
        """
            Convert a python string to a var
        """
        raise NotImplementedError


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
    def serialize(cls, value, **kwargs):
        """
            True is serialized to "1" to take less space
            same for False, with "0"
        """
        if value:
            return "1"
        else:
            return "0"

    @classmethod
    def deserialize(cls, value, **kwargs):

        if value in cls.true:
            return True

        elif value in cls.false:
            return False

        else:
            raise cls.exception("Value {0} can't be deserialized to a Boolean".format(value))


class IntSerializer(BaseSerializer):

    @classmethod
    def serialize(cls, value, **kwargs):
        if not isinstance(value, int):
            raise cls.exception('IntSerializer can only serialize int values')

        return value.__str__()

    @classmethod
    def deserialize(cls, value, **kwargs):
        try:
            return int(value)
        except:
            raise cls.exception("Value {0} cannot be converted to int")

from django.template import defaultfilters

class StringSerializer(BaseSerializer):

    @classmethod
    def serialize(cls, value, **kwargs):
        if not isinstance(value, basestring):
            raise cls.exception("Cannot serialize, value {0} is not a string".format(value))

        if kwargs.get("escape_html", False):
            return defaultfilters.force_escape(value)
        else:
            return value

    @classmethod
    def deserialize(cls, value, **kwargs):
        if not isinstance(value, basestring):
            raise cls.exception("Cannot deserialize, value {0} is not a string".format(value))

        return value