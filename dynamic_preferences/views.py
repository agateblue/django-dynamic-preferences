from django.views.generic import TemplateView, FormView
from dynamic_preferences import global_preferences, site_preferences, user_preferences
from django.http import Http404
from dynamic_preferences.forms import PreferenceForm


class PreferenceMixin(object):
    registry = None
    app = None
    preferences = None

    def get_context_data(self, **kwargs):
        context = super(PreferenceMixin, self).get_context_data(**kwargs)
        context['preferences_registry'] = self.registry

        context['preferences'] = self.preferences or self.get_preferences()

        return context

    def get_preferences(self):
        try:
            return self.registry.preferences(app=self.app)
        except KeyError:
            # App does not exist or does not have any registered preferences
            raise Http404


class PreferenceList(PreferenceMixin, TemplateView):
    pass


class AppPreferenceList(PreferenceMixin, FormView):

    form_class = PreferenceForm
    success_url = "/"

    def setup(self):

        self.app = self.app or self.kwargs.get("app", None)
        self.preferences = self.get_preferences()

    def get(self, request, *args, **kwargs):

        self.setup()
        return super(AppPreferenceList, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        self.setup()
        return super(AppPreferenceList, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """

        kwargs = super(AppPreferenceList, self).get_form_kwargs()
        kwargs['preferences'] = self.preferences
        return kwargs

    def form_valid(self, form, **kwargs):
        # Save preference value in DB



        return super(AppPreferenceList, self).form_valid(form)
class GlobalPreferenceList(PreferenceList):
    registry = global_preferences
    template_name = "dynamic_preferences/list.html"


class GlobalAppPreferenceList(AppPreferenceList):
    registry = global_preferences
    template_name = "dynamic_preferences/app.list.html"