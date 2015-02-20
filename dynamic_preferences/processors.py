from .models import GlobalPreferenceModel, UserPreferenceModel

def global_preferences(request):
    """
        Pass the values of global preferences to template context.
        You can then access value with `global_preferences.<section>.<name>`
    """
    return {'global_preferences': GlobalPreferenceModel.objects.to_dict()}


def user_preferences(request):
    """
        Pass the values of `request.user` preferences to template context.
        You can then access value with `user_preferences.<section>.<name>`
        If user is not logged in, an empty dictionary will be passed to context 
    """ 

    user = request.user
    if user.is_authenticated():
        return {'user_preferences': UserPreferenceModel.objects.to_dict(instance=user)}

    return {}