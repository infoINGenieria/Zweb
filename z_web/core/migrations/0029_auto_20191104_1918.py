# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20181017_0819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='obras',
            name='deposito',
            field=models.CharField(verbose_name='N° Depósito', max_length=16, unique=True, null=True),
        ),
    ]
