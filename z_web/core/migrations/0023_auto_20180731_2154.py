# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20180701_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipos',
            name='es_alquilado',
            field=models.BooleanField(verbose_name='es equipo alquilado', default=False),
        ),
        migrations.AddField(
            model_name='equipos',
            name='fecha_baja',
            field=models.DateField(verbose_name='fecha de baja', null=True),
        ),
    ]
