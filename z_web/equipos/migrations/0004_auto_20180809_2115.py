# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipos', '0003_asistenciaequipo_historicalasistenciaequipo_historicalcostoequipovalores_historicalequipoalquiladova'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asistenciaequipo',
            name='dia',
            field=models.DateField(verbose_name='día', unique=True),
        ),
        migrations.AlterField(
            model_name='historicalasistenciaequipo',
            name='dia',
            field=models.DateField(verbose_name='día', db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='registroasistenciaequipo',
            unique_together=set([('asistencia', 'equipo', 'centro_costo')]),
        ),
    ]
