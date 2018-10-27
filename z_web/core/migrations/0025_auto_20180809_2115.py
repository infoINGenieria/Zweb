# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_equipos_excluir_costos_taller'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipos',
            name='fecha_baja',
            field=models.DateField(verbose_name='fecha de baja', blank=True, null=True),
        ),
    ]
