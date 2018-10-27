# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_userextension_unidades_negocio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userextension',
            name='unidad_negocio',
        ),
        migrations.AlterField(
            model_name='userextension',
            name='unidades_negocio',
            field=models.ManyToManyField(verbose_name='unidades de negocio', related_name='usuarios_de_la_unidad', to='organizacion.UnidadNegocio'),
        ),
    ]
