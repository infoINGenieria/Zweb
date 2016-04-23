# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20160410_1234'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerfilTecnico',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('nombre', models.CharField(verbose_name='nombre', max_length=255)),
                ('tiene_comida', models.BooleanField(default=True, verbose_name='tiene comida')),
                ('tiene_vianda', models.BooleanField(default=True, verbose_name='tiene vianda')),
                ('tiene_desarraigo', models.BooleanField(default=True, verbose_name='tiene desarraigo')),
                ('limite_vianda_doble', models.FloatField(default=2, verbose_name='limite vianda doble')),
                ('tiene_registro', models.BooleanField(default=True, verbose_name='tiene registro')),
                ('tiene_equipo', models.BooleanField(default=True, verbose_name='tiene equipo')),
                ('descuenta_francos', models.BooleanField(default=False, verbose_name='Se utiliza para francos')),
                ('descuenta_licencias', models.BooleanField(default=False, verbose_name='Se utiliza para licencias anuales')),
                ('es_cc', models.BooleanField(default=False, help_text='Si está seleccionada, la obra es considerada un Centro de Costos (CC)', verbose_name='Tratar como CC')),
                ('prorratea_costos', models.BooleanField(default=False, help_text='Si está seleccionada, los costos se prorratean en los demás CC', verbose_name='¿Prorratea Costos?')),
            ],
            options={
                'verbose_name_plural': 'perfiles técnicos',
                'verbose_name': 'perfíl técnico',
            },
        ),
    ]
