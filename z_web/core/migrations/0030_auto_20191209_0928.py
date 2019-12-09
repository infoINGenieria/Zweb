# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20191104_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='obras',
            name='deposito',
            field=models.CharField(verbose_name='N° Depósito', max_length=16, blank=True, null=True),
        ),
    ]
