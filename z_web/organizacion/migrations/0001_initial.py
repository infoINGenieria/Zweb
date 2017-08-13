# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UnidadNegocio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('codigo', models.CharField(verbose_name='código', max_length=12, unique=True)),
                ('nombre', models.CharField(verbose_name='nombre', max_length=255)),
                ('activa', models.BooleanField(verbose_name='activa', default=True)),
                ('observaciones', models.TextField()),
            ],
            options={
                'verbose_name': 'unidad de negocio',
                'verbose_name_plural': 'unidades de negocio',
            },
        ),
    ]
