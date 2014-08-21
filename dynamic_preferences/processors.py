from models import global_preferences as gb, user_preferences as up

def global_preferences(request):
    """
        Pass the values of global preferences to template context.
        You can then access value with `global_preferences.<section>.<name>`
    """
    return {'global_preferences': gb.to_dict()}


def user_preferences(request):
    """
        Pass the values of `request.user` preferences to template context.
        You can then access value with `user_preferences.<section>.<name>`
        If user is not logged in, an empty dictionary will be passed to context 
    """ 

    user = request.user
    if user.is_authenticated():
        return {'user_preferences': up.to_dict(user=user)}

    return {}