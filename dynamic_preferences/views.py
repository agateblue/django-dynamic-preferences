from django.views.generic import TemplateView, FormView
from forms import preference_form_builder, user_preference_form_builder
from registries import user_preferences_registry, global_preferences_registry
from models import user_preferences, global_preferences

class GlobalPreferenceMixin(object):
    """
        Pass the values of global preferences to template context.
        You can then access value with `global_preferences.<section>.<name>`
    """ 
    def get_context_data(self, *args, **kwargs):

        context = super(GlobalPreferenceMixin, self).get_context_data(*args, **kwargs)

        context['global_preferences'] = global_preferences.to_dict()

        return context

class GlobalPreferenceView(GlobalPreferenceMixin, TemplateView):
    template_name = "dynamic_preferences/testcontext.html"

class UserPreferenceMixin(object):
    """
        Pass the values of `request.user` preferences to template context.
        You can then access value with `user_preferences.<section>.<name>`
        If user is not logged in, an empty dictionary will be passed to context 
    """ 
    def get_context_data(self, *args, **kwargs):

        context = super(UserPreferenceMixin, self).get_context_data(*args, **kwargs)

        user = self.request.user
        if user.is_authenticated():
            context['user_preferences'] = user_preferences.to_dict(user=user)

        return context
    
class UserPreferenceView(UserPreferenceMixin, TemplateView):
    template_name = "dynamic_preferences/testcontext.html"

class PreferenceMixin(UserPreferenceMixin, GlobalPreferenceMixin):
    """Include both GlobalPreferences and preferences from request.user"""
    pass

class PreferenceView(PreferenceMixin, TemplateView):
    template_name = "dynamic_preferences/testcontext.html"

class PreferenceFormView(FormView):
    """Display a form for updating preferences of the given section provided via URL arg.
    If no section is provided, will dispaly a form for all fields of a given registry.
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
        form_class = user_preference_form_builder(user=self.request.user, section=section)
        return form_class