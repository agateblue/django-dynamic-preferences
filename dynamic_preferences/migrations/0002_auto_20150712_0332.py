# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("dynamic_preferences", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="globalpreferencemodel",
            name="name",
            field=models.CharField(max_length=150, db_index=True),
        ),
        migrations.AlterField(
            model_name="globalpreferencemodel",
            name="section",
            field=models.CharField(
                max_length=150, blank=True, db_index=True, default=None, null=True
            ),
        ),
    ]
