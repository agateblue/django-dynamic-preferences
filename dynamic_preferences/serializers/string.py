from dynamic_preferences.serializers import BaseSerializer
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