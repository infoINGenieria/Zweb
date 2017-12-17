# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0035_auto_20171216_1235'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certificacionitem',
            name='adicional',
        ),
        migrations.AlterField(
            model_name='certificacionitem',
            name='observaciones',
            field=models.CharField(verbose_name='observaciones', max_length=255, blank=True, null=True),
        ),
    ]
