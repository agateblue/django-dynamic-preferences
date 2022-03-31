# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="GlobalPreferenceModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                        auto_created=True,
                    ),
                ),
                (
                    "section",
                    models.CharField(
                        blank=True,
                        default=None,
                        null=True,
                        max_length=150,
                        db_index=True,
                    ),
                ),
                ("name", models.CharField(max_length=150, db_index=True)),
                ("raw_value", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name_plural": "global preferences",
                "verbose_name": "global preference",
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="globalpreferencemodel",
            unique_together=set([("section", "name")]),
        ),
    ]
