REST API
========

Dynamic preferences provides an optional integration with Django REST Framework:

- Serializers you can use for global and user preferences (or to extend for your own preferences)
- Viewsets you can use for global and user preferences (or to extend for your own preferences)

Getting started
---------------

The easiest way to offer API endpoints to manage preferences in your project is to use
bundled viewsets in your ``urls.py``:

.. code-block:: python

    from django.urls import include, re_path
    from rest_framework import routers

    from dynamic_preferences.api.viewsets import GlobalPreferencesViewSet
    from dynamic_preferences.users.viewsets import UserPreferencesViewSet


    router = routers.SimpleRouter()
    router.register(r'global', GlobalPreferencesViewSet, 'global')

    # Uncomment this one if you use user preferences
    # router.register(r'user', UserPreferencesViewSet, 'user')

    api_patterns = [
        re_path(r'^preferences/', include(router.urls, namespace='preferences'))

    ]
    urlpatterns = [
        # your other urls here
        re_path(r'^api/', include(api_patterns, namespace='api'))
    ]


Endpoints
---------

For each preference viewset, the following endpoints are available:

Example reverse and urls are given according to the previous snippet. You'll
have to adapt them to your own URL namespaces and structure.

List
^^^^^^^

- Methods: GET
- Returns a list of preferences
- Reverse example: ``reverse('api:preferences:global-list')``
- URL examples:

  - List all preferences

    ``/api/preferences/global/``

  - List all preferences under ``blog`` section

    ``/api/preferences/global/?section=blog``

Detail
^^^^^^^

- Methods: GET, PATCH
- Get or update a single preference
- Reverse example: ``reverse('api:preferences:global-detail', kwargs={'pk': 'section__name'})``
- URL example: ``/api/preferences/global/section__name``

If you call this endpoint via PATCH HTTP method, you can update the preference value.
The following payload is expected::


    {
        value: 'new_value'
    }

.. note::

    When updating the preference value, the underlying serializers will call
    the preference field validators, and the preference ``validate`` method,
    if any is available.

Bulk
^^^^^

- Methods: POST
- Update multiple preferences at once
- Reverse example: ``reverse('api:preferences:global-bulk')``
- URL example: ``/api/preferences/global/bulk``

If you call this endpoint via POST HTTP method, you can update the the value
of multiple preferences at once. Example payload::

    {
        section1__name1: 'new_value',
        section2__name2: false,
    }

This will update the preferences whose identifiers match ``section1__name1``
and ``section2__name2`` with the corresponding values.

.. note::

    Validation will be called for each preferences, ans save will only occur
    if no error happens.

A note about permissions
^^^^^^^^^^^^^^^^^^^^^^^^

- ``GlobalPreferencesViewSet`` will check the user has the ``dynamic_preferences.change_globalpreferencemodel`` permission
- ``UserPreferencesViewSet`` will check the user is logged in and only allow him to edit his own preferences.
