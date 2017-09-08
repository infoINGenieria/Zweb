# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0022_auto_20170827_2358'),
    ]

    operations = [
        migrations.AddField(
            model_name='costo',
            name='es_proyeccion',
            field=models.BooleanField(verbose_name='Es una proyección', default=False),
        ),
    ]
