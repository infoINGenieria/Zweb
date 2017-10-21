# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0032_auto_20171016_2115'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='certificacion',
            options={'verbose_name': 'certificación', 'verbose_name_plural': 'certificaciones', 'permissions': (('can_manage_certificacion', 'Puede gestionar certificaciones'),)},
        ),
        migrations.AlterUniqueTogether(
            name='certificacion',
            unique_together=set([('periodo', 'obra', 'es_proyeccion')]),
        ),
    ]
