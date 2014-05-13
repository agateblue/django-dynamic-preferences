from django.views.generic import TemplateView
from dynamic_preferences import global_preferences, site_preferences, user_preferences


class PreferenceList(TemplateView):
    registry = None

    def get_context_data(self, **kwargs):
        context = super(PreferenceList, self).get_context_data(**kwargs)
        context['preferences_registry'] = self.registry
        context['preferences'] = self.get_preferences()
        return context

    def get_preferences(self):
        app = self.kwargs.get("app", None)
        print(self.kwargs)
        return self.registry.preferences(app)


class GlobalPreferenceList(PreferenceList):
    registry = global_preferences
    template_name = "dynamic_preferences/list.html"