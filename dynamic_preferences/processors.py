from .registries import global_preferences_registry as gpr


def global_preferences(request):
    """
        Pass the values of global preferences to template context.
        You can then access value with `global_preferences.<section>.<name>`
    """
    manager = gpr.manager()
    return {'global_preferences': manager.all()}
