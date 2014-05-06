from dynamic_preferences.serializers import BaseSerializer


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
