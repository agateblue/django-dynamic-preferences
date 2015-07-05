from . import user_preferences_registry as upr, global_preferences_registry as gpr

def global_preferences(request):
    """
        Pass the values of global preferences to template context.
        You can then access value with `global_preferences.<section>.<name>`
    """
    getter = gpr.getter()
    return {'global_preferences': getter.all()}


def user_preferences(request):
    """
        Pass the values of `request.user` preferences to template context.
        You can then access value with `user_preferences.<section>.<name>`
        If user is not logged in, an empty dictionary will be passed to context
    """

    user = request.user
    if user.is_authenticated():
        getter = upr.getter(instance=user)
        return {'user_preferences': getter.all()}

    return {}
