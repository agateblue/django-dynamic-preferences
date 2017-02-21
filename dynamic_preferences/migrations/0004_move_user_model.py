# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    """
    Migration to move the user preferences to a dedicated app, see #33
    Borrowed from http://stackoverflow.com/a/26472482/2844093
    """
    dependencies = [
        ('dynamic_preferences', '0003_auto_20151223_1407'),
    ]

    database_operations = [
        migrations.AlterModelTable(
            'UserPreferenceModel', 'dynamic_preferences_users_userpreferencemodel')
    ]

    state_operations = [
        migrations.DeleteModel('UserPreferenceModel')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]
