from ..views import PreferenceFormView
from .forms import user_preference_form_builder
from .registries import user_preferences_registry


class UserPreferenceFormView(PreferenceFormView):
    """
    Will pass `request.user` to form_builder
    """
    registry = user_preferences_registry

    def get_form_class(self, *args, **kwargs):
        section = self.kwargs.get('section', None)
        form_class = user_preference_form_builder(
            instance=self.request.user, section=section)
        return form_class
