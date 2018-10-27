# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20180809_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipos',
            name='implica_mo_logistica',
            field=models.BooleanField(verbose_name='implica mano de obra logística', default=False, help_text='Seleccionar si este equipo prorratea mano de obra de carretones'),
        ),
    ]
