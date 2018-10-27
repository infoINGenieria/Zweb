# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_obras_deposito'),
    ]

    operations = [
        migrations.AlterField(
            model_name='obras',
            name='deposito',
            field=models.IntegerField(verbose_name='N° Depósito', unique=True, null=True),
        ),
    ]
