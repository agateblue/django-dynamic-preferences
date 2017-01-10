from django.views.generic import TemplateView, FormView
from .forms import preference_form_builder, user_preference_form_builder
from .registries import user_preferences_registry


"""Todo : remove these views and use only context processors"""
class RegularTemplateView(TemplateView):
    """Used for testing context"""
    template_name = "dynamic_preferences/testcontext.html"


class PreferenceFormView(FormView):
    """Display a form for updating preferences of the given section provided via URL arg.
    If no section is provided, will display a form for all fields of a given registry.
    """

    #: the registry for preference lookups
    registry = None

    #: will be used by :py:func:`forms.preference_form_builder` to create the form
    form_class = None

    template_name = "dynamic_preferences/form.html"

    def get_form_class(self, *args, **kwargs):
        section = self.kwargs.get('section', None)
        form_class = preference_form_builder(self.form_class, section=section)
        return form_class

    def get_context_data(self, *args, **kwargs):

        context = super(PreferenceFormView, self).get_context_data(*args, **kwargs)

        context['registry'] = self.registry

        return context

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):

        form.update_preferences()
        return super(PreferenceFormView, self).form_valid(form)

class UserPreferenceFormView(PreferenceFormView):
    """
    Will pass `request.user` to form_builder
    """
    registry = user_preferences_registry

    def get_form_class(self, *args, **kwargs):
        section = self.kwargs.get('section', None)
        form_class = user_preference_form_builder(instance=self.request.user, section=section)
        return form_class
