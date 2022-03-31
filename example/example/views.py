from dynamic_preferences.registries import global_preferences_registry
from django.shortcuts import render

# We instantiate a manager for our global preferences
global_preferences = global_preferences_registry.manager()

# Now, we can use it to retrieve our preferences
# the lookup for a preference has the following form: <section>__<name>


def myview(request):
    presentation = global_preferences["general__presentation"]

    return render(
        request,
        "example.html",
        {
            "presentation": presentation,
        },
    )
