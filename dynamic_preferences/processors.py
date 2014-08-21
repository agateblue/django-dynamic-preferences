from models import global_preferences, user_preferences

def global_preferences_objects(request):
    """
        Pass the values of global preferences to template context.
        You can then access value with `global_preferences.<section>.<name>`
    """
    return {'global_preferences': global_preferences.to_dict()}


def user_preferences_objects(request):
    """
        Pass the values of `request.user` preferences to template context.
        You can then access value with `user_preferences.<section>.<name>`
        If user is not logged in, an empty dictionary will be passed to context 
    """ 

    user = request.user
    if user.is_authenticated():
        return {'user_preferences': user_preferences.to_dict(user=user)}

    return {}