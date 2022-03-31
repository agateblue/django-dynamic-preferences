from django.views.generic import TemplateView, FormView
from django.http import Http404
from .forms import preference_form_builder


"""Todo : remove these views and use only context processors"""


class RegularTemplateView(TemplateView):
    """Used for testing context"""

    template_name = "dynamic_preferences/testcontext.html"


class PreferenceFormView(FormView):
    """
    Display a form for updating preferences of the given
    section provided via URL arg.
    If no section is provided, will display a form for all
    fields of a given registry.
    """

    #: the registry for preference lookups
    registry = None

    #: will be used by :py:func:`forms.preference_form_builder`
    # to create the form
    form_class = None
    template_name = "dynamic_preferences/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.section_name = kwargs.get("section", None)
        if self.section_name:
            try:
                self.section = self.registry.section_objects[self.section_name]
            except KeyError:
                raise Http404
        else:
            self.section = None
        return super(PreferenceFormView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self, *args, **kwargs):
        form_class = preference_form_builder(self.form_class, section=self.section_name)
        return form_class

    def get_context_data(self, *args, **kwargs):
        context = super(PreferenceFormView, self).get_context_data(*args, **kwargs)
        context["registry"] = self.registry
        context["section"] = self.section

        return context

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):

        form.update_preferences()
        return super(PreferenceFormView, self).form_valid(form)
