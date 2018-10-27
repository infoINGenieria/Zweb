# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipos', '0010_auto_20181015_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipoalquiladovalores',
            name='comentarios',
            field=models.TextField(verbose_name='comentarios', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalequipoalquiladovalores',
            name='comentarios',
            field=models.TextField(verbose_name='comentarios', blank=True, null=True),
        ),
    ]
