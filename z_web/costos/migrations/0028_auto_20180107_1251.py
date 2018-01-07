# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0027_auto_20180102_2154'),
        ('proyecciones', '0006_auto_20180107_1240'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CostoProyeccion',
        ),
        migrations.DeleteModel(
            name='CostoReal',
        ),
        migrations.RemoveField(
            model_name='costo',
            name='es_proyeccion',
        ),
    ]
