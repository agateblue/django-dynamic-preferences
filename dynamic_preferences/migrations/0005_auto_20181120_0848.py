# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dynamic_preferences", "0004_move_user_model"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="globalpreferencemodel",
            options={
                "verbose_name": "Global preference",
                "verbose_name_plural": "Global preferences",
            },
        ),
        migrations.AlterField(
            model_name="globalpreferencemodel",
            name="name",
            field=models.CharField(db_index=True, max_length=150, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="globalpreferencemodel",
            name="raw_value",
            field=models.TextField(blank=True, null=True, verbose_name="Raw Value"),
        ),
    ]
