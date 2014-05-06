from dynamic_preferences.serializers import BaseSerializer


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



