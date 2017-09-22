from rest_framework import serializers
from dynamic_preferences.models import GlobalPreferenceModel


class PreferenceValueField(serializers.Field):
    def get_attribute(self, o):
        return o

    def to_representation(self, o):
        return o.preference.api_repr(
            o.value
        )

    def to_internal_value(self, data):
        return data


class PreferenceSerializer(serializers.Serializer):

    section = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    identifier = serializers.SerializerMethodField()
    default = serializers.SerializerMethodField()
    value = PreferenceValueField()
    verbose_name = serializers.SerializerMethodField()
    help_text = serializers.SerializerMethodField()
    additional_data = serializers.SerializerMethodField()
    field = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'default',
            'value',
            'verbose_name',
            'help_text',
        ]

    def get_default(self, o):
        return o.preference.api_repr(
            o.preference.get('default')
        )

    def get_verbose_name(self, o):
        return o.preference.get('verbose_name')

    def get_identifier(self, o):
        return o.preference.identifier()

    def get_help_text(self, o):
        return o.preference.get('help_text')

    def get_additional_data(self, o):
        return o.preference.get_api_additional_data()

    def get_field(self, o):
        return o.preference.get_api_field_data()

    def validate_value(self, value):
        """
        We call validation from the underlying form field
        """
        field = self.instance.preference.setup_field()
        value = field.to_python(value)
        field.validate(value)
        field.run_validators(value)
        return value

    def update(self, instance, validated_data):
        instance.value = validated_data['value']
        instance.save()
        return instance


class GlobalPreferenceSerializer(PreferenceSerializer):
    pass
