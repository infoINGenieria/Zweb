# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_equipos_implica_mo_logistica'),
    ]

    operations = [
        migrations.AddField(
            model_name='obras',
            name='deposito',
            field=models.IntegerField(verbose_name='N° Depósito', null=True),
        ),
    ]
