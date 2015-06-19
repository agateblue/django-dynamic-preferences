from . import user_preferences as up, global_preferences as gp

def global_preferences(request):
    """
        Pass the values of global preferences to template context.
        You can then access value with `global_preferences.<section>.<name>`
    """
    getter = gp.getter()
    return {'global_preferences': getter.all()}


def user_preferences(request):
    """
        Pass the values of `request.user` preferences to template context.
        You can then access value with `user_preferences.<section>.<name>`
        If user is not logged in, an empty dictionary will be passed to context
    """

    user = request.user
    if user.is_authenticated():
        getter = up.getter(instance=user)
        return {'user_preferences': getter.all()}

    return {}
