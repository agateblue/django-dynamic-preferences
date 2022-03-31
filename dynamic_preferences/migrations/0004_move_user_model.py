# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    """
    Migration to move the user preferences to a dedicated app, see #33
    Borrowed from http://stackoverflow.com/a/26472482/2844093
    """

    dependencies = [
        ("dynamic_preferences", "0003_auto_20151223_1407"),
    ]

    # cf https://github.com/agateblue/django-dynamic-preferences/pull/142
    operations = []
