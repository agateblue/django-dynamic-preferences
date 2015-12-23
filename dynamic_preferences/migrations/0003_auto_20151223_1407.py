# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_preferences', '0002_auto_20150712_0332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='globalpreferencemodel',
            name='name',
            field=models.CharField(max_length=150, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='globalpreferencemodel',
            name='section',
            field=models.CharField(max_length=150, null=True, default=None, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userpreferencemodel',
            name='name',
            field=models.CharField(max_length=150, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userpreferencemodel',
            name='section',
            field=models.CharField(max_length=150, null=True, default=None, db_index=True, blank=True),
            preserve_default=True,
        ),
    ]
