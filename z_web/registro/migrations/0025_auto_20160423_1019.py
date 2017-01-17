# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20160410_1234'),
        ('registro', '0024_auto_20160416_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='ajustecombustible',
            name='obra',
            field=models.ForeignKey(default=9, related_name='ajustes_combustibles_x_obra', to='core.Obras'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='ajustecombustible',
            unique_together=set([('periodo', 'obra')]),
        ),
    ]
