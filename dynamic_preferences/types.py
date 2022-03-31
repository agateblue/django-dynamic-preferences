"""
You'll find here the final, concrete classes of preferences you can use
in your own project.

"""
from django import forms
from django.db.models.signals import pre_delete

from django.core.files.storage import default_storage

from .preferences import AbstractPreference, Section
from .exceptions import MissingModel
from dynamic_preferences.serializers import *
from dynamic_preferences.settings import preferences_settings


class BasePreferenceType(AbstractPreference):
    """
    Used as a base for all other preference classes. You should subclass
    this one if you want to implement your own preference.
    """

    field_class = None
    """
    A form field that will be used to display and edit the preference
    use a class, not an instance.

    :Example:

    .. code-block:: python

        from django import forms

        class MyPreferenceType(BasePreferenceType):
            field_class = forms.CharField
    """

    #: A serializer class (see dynamic_preferences.serializers)
    serializer = None

    field_kwargs = {}
    """
    Additional kwargs to be passed to the form field.

    :Example:

    .. code-block:: python

        class MyPreference(StringPreference):

            field_kwargs = {
                'required': False,
                'initial': 'Hello there'
            }
    """

    @property
    def initial(self):
        return self.get_initial()

    def get_initial(self):
        """
        :return:
            initial data for form field
            from field_attribute['initial'] or default
        """
        return self.field_kwargs.get("initial", self.get("default"))

    @property
    def field(self):
        """
        :return:
            an instance of a form field for this preference, with
            the correct configuration (widget, initial value, validators...)
        """
        return self.setup_field()

    def setup_field(self, **kwargs):
        field_class = self.get("field_class")
        field_kwargs = self.get_field_kwargs()
        field_kwargs.update(kwargs)
        return field_class(**field_kwargs)

    def get_field_kwargs(self):
        """
        Return a dict of arguments to use as parameters for the field
        class instianciation.

        This will use :py:attr:`field_kwargs` as a starter,
        and use sensible defaults for a few attributes:

        - :py:attr:`instance.verbose_name` for the field label
        - :py:attr:`instance.help_text` for the field help text
        - :py:attr:`instance.widget` for the field widget
        - :py:attr:`instance.required` defined if the value is required or not
        - :py:attr:`instance.initial` defined if the initial value
        """
        kwargs = self.field_kwargs.copy()
        kwargs.setdefault("label", self.get("verbose_name"))
        kwargs.setdefault("help_text", self.get("help_text"))
        kwargs.setdefault("widget", self.get("widget"))
        kwargs.setdefault("required", self.get("required"))
        kwargs.setdefault("initial", self.initial)
        kwargs.setdefault("validators", [])
        kwargs["validators"].append(self.validate)
        return kwargs

    def api_repr(self, value):
        """
        Used only to represent a preference value using Rest Framework
        """
        return value

    def get_api_additional_data(self):
        """
        Additional data to serialize for use on front-end side, for example
        """
        return {}

    def get_api_field_data(self):
        """
        Field data to serialize for use on front-end side, for example
        will include choices available for a choice field
        """
        field = self.setup_field()
        d = {
            "class": field.__class__.__name__,
            "widget": {"class": field.widget.__class__.__name__},
        }

        try:
            d["input_type"] = field.widget.input_type
        except AttributeError:
            # some widgets, such as Select do not have an input type
            # in django < 1.11
            d["input_type"] = None

        return d

    def validate(self, value):
        """
        Used to implement custom cleaning logic for use in forms
        and serializers. The method will be passed as a validator to
        the preference form field.

        :Example:

        .. code-block:: python

            def validate(self, value):
                if value == '42':
                    raise ValidationError('Wrong value!')
        """
        return


class BooleanPreference(BasePreferenceType):
    """
    A preference type that stores a boolean.
    """

    field_class = forms.BooleanField
    serializer = BooleanSerializer
    required = False


class IntegerPreference(BasePreferenceType):
    """
    A preference type that stores an integer.
    """

    field_class = forms.IntegerField
    serializer = IntegerSerializer


IntPreference = IntegerPreference


class DecimalPreference(BasePreferenceType):
    """
    A preference type that stores a :py:class:`decimal.Decimal`.
    """

    field_class = forms.DecimalField
    serializer = DecimalSerializer


class FloatPreference(BasePreferenceType):
    """
    A preference type that stores a float.
    """

    field_class = forms.FloatField
    serializer = FloatSerializer


class StringPreference(BasePreferenceType):
    """
    A preference type that stores a string.
    """

    field_class = forms.CharField
    serializer = StringSerializer


class LongStringPreference(StringPreference):
    """
    A preference type that stores a string, but with a textarea widget.
    """

    widget = forms.Textarea


class ChoicePreference(BasePreferenceType):
    """
    A preference type that stores a string among a list of choices.
    """

    choices = ()
    """
    Expects the same values as for django :py:class:`forms.ChoiceField`.

    :Example:

    .. code-block:: python

        class MyChoicePreference(ChoicePreference):
            choices = [
                ('c', 'Carrot'),
                ('t', 'Tomato'),
            ]
    """
    field_class = forms.ChoiceField
    serializer = StringSerializer

    def get_field_kwargs(self):
        field_kwargs = super(ChoicePreference, self).get_field_kwargs()
        field_kwargs["choices"] = self.get("choices") or self.field_attribute["initial"]
        return field_kwargs

    def get_api_additional_data(self):
        d = super(ChoicePreference, self).get_api_additional_data()
        d["choices"] = self.get("choices")
        return d

    def get_choice_values(self):
        return [c[0] for c in self.get("choices")]

    def validate(self, value):
        if value not in self.get_choice_values():
            raise forms.ValidationError("{} is not a valid choice".format(value))


def create_deletion_handler(preference):
    """
    Will generate a dynamic handler to purge related preference
    on instance deletion
    """

    def delete_related_preferences(sender, instance, *args, **kwargs):
        queryset = preference.registry.preference_model.objects.filter(
            name=preference.name, section=preference.section
        )
        related_preferences = queryset.filter(
            raw_value=preference.serializer.serialize(instance)
        )
        related_preferences.delete()

    return delete_related_preferences


class ModelChoicePreference(BasePreferenceType):
    """
    A preference type that stores a reference to a model instance.

    :Example:

    .. code-block:: python

        from myapp.blog.models import BlogEntry

        @registry.register
        class FeaturedEntry(ModelChoicePreference):
            section = Section('blog')
            name = 'featured_entry'
            queryset = BlogEntry.objects.filter(status='published')

        blog_entry = BlogEntry.objects.get(pk=12)
        manager['blog__featured_entry'] = blog_entry

        # accessing the value will return the model instance
        assert manager['blog__featured_entry'].pk == 12

    .. note::

        You should provide either the :py:attr:`queryset` or :py:attr:`model`
        attribute
    """

    field_class = forms.ModelChoiceField
    serializer_class = ModelSerializer

    model = None
    """
    Which model class to link the preference to. You can skip this if you
    define the :py:attr:`queryset` attribute.
    """

    queryset = None
    """
    A queryset to filter available model instances.
    """
    signals_handlers = {}

    def __init__(self, *args, **kwargs):
        super(ModelChoicePreference, self).__init__(*args, **kwargs)

        if self.model is not None:
            # Set queryset following model attribute
            self.queryset = self.model.objects.all()
        elif self.queryset is not None:
            # Set model following queryset attribute
            self.model = self.queryset.model
        else:
            raise MissingModel

        self.serializer = self.serializer_class(self.model)

        self._setup_signals()

    def _setup_signals(self):
        handler = create_deletion_handler(self)
        # We need to keep a reference to the handler or it will cause
        # weakref to die and our handler will not be called
        self.signals_handlers["pre_delete"] = [handler]
        pre_delete.connect(handler, sender=self.model)

    def get_field_kwargs(self):
        kw = super(ModelChoicePreference, self).get_field_kwargs()
        kw["queryset"] = self.get("queryset")
        return kw

    def api_repr(self, value):
        if not value:
            return None
        if value.__class__.__name__ == "QuerySet":
            return [val.pk for val in value]
        return value.pk


class ModelMultipleChoicePreference(ModelChoicePreference):
    """
    A preference type that stores a reference list to the model instances.

    :Example:

    .. code-block:: python

        from myapp.blog.models import BlogEntry

        @registry.register
        class FeaturedEntries(ModelMultipleChoicePreference):
            section = Section('blog')
            name = 'featured_entries'
            queryset = BlogEntry.objects.all()

        blog_entries = BlogEntry.objects.filter(status='published')
        manager['blog__featured_entries'] = blog_entries

        # accessing the value will return the model queryset
        assert manager['blog__featured_entries'] == blog_entries

    .. note::

        You should provide either the :py:attr:`queryset` or :py:attr:`model`
        attribute
    """

    serializer_class = ModelMultipleSerializer
    field_class = forms.ModelMultipleChoiceField

    def _setup_signals(self):
        pass


class FilePreference(BasePreferenceType):
    """
    A preference type that stores a a reference to a model.

    :Example:

    .. code-block:: python

        from django.core.files.uploadedfile import SimpleUploadedFile

        @registry.register
        class Logo(FilePreference):
            section = Section('blog')
            name = 'logo'

        logo = SimpleUploadedFile(
            "logo.png", b"file_content", content_type="image/png")
        manager['blog__logo'] = logo

        # accessing the value will return a FieldFile object, just as
        # django.db.models.FileField
        assert manager['blog__logo'].read() == b'file_content'

        manager['blog__logo'].delete()

    """

    field_class = forms.FileField
    serializer_class = FileSerializer
    default = None

    @property
    def serializer(self):
        """
        The serializer need additional data about the related preference
        to upload file to correct directory
        """
        return self.serializer_class(self)

    def get_field_kwargs(self):
        kwargs = super(FilePreference, self).get_field_kwargs()
        kwargs["required"] = self.get("required", False)
        return kwargs

    def get_upload_path(self):
        return os.path.join(
            preferences_settings.FILE_PREFERENCE_UPLOAD_DIR, self.identifier()
        )

    def get_file_storage(self):
        """
        Override this method if you want to use a custom storage
        """
        return default_storage

    def api_repr(self, value):
        if value:
            return value.url


class DurationPreference(BasePreferenceType):
    """
    A preference type that stores a timedelta.
    """

    field_class = forms.DurationField
    serializer = DurationSerializer

    def api_repr(self, value):
        return duration_string(value)


class DatePreference(BasePreferenceType):
    """
    A preference type that stores a date.
    """

    field_class = forms.DateField
    serializer = DateSerializer

    def api_repr(self, value):
        return value.isoformat()


class DateTimePreference(BasePreferenceType):
    """
    A preference type that stores a datetime.
    """

    field_class = forms.DateTimeField
    serializer = DateTimeSerializer

    def api_repr(self, value):
        return value.isoformat()


class TimePreference(BasePreferenceType):
    """
    A preference type that stores a time.
    """

    field_class = forms.TimeField
    serializer = TimeSerializer

    def api_repr(self, value):
        return value.isoformat()


class MultipleChoicePreference(ChoicePreference):
    """
    A preference type that stores multiple strings among a list of choices.

    :Example:

    .. code-block:: python

        @registry.register
        class FeaturedEntries(MultipleChoicePreference):
            section = Section('blog')
            name = 'featured_entries'
            choices = [
                ('c', 'Carrot'),
                ('t', 'Tomato'),
            ]

    .. note::

       Internally, the selected choices are stored as a string, separated by a
       separator. The separator defaults to ','. The way this is implemented still
       is sae also on keys that cotain the separator, but if in doubt, you can still
       set the :py:attr:`separator` to any other character.
    """

    widget = forms.CheckboxSelectMultiple
    field_class = forms.MultipleChoiceField
    serializer = MultipleSerializer

    def validate(self, value):
        for v in value:
            super().validate(v)
