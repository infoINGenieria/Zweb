# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0025_auto_20170910_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avanceobra',
            name='centro_costo',
            field=models.ForeignKey(verbose_name='centro de costo', related_name='mis_avances', to='core.Obras'),
        ),
        migrations.AlterUniqueTogether(
            name='avanceobra',
            unique_together=set([('periodo', 'centro_costo', 'es_proyeccion')]),
        ),
    ]
