# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20170813_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfoObra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('cliente', models.CharField(verbose_name='cliente', max_length=255, blank=True, null=True)),
                ('gerente_proyecto', models.CharField(verbose_name='gerente de proyecto', max_length=255, blank=True, null=True)),
                ('jefe_obra', models.CharField(verbose_name='jefe de obra', max_length=255, blank=True, null=True)),
                ('planificador', models.CharField(verbose_name='planificador', max_length=255, blank=True, null=True)),
                ('control_gestion', models.CharField(verbose_name='control de gestión', max_length=255, blank=True, null=True)),
                ('inicio_comercial', models.DateField(verbose_name='inicio según etapa comercial', null=True)),
                ('inicio_contractual', models.DateField(verbose_name='inicio contractual', null=True)),
                ('inicio_real', models.DateField(verbose_name='inicio real', null=True)),
                ('plazo_comercial', models.PositiveSmallIntegerField(verbose_name='plazo comercial', null=True, help_text='meses')),
                ('plazo_contractual', models.PositiveSmallIntegerField(verbose_name='plazo contractual', null=True, help_text='meses')),
                ('plazo_con_ampliaciones', models.PositiveSmallIntegerField(verbose_name='plazo con ampliaciones', null=True, help_text='meses')),
                ('fin_previsto_comercial', models.DateField(verbose_name='fin previsto comercial', null=True)),
                ('fin_contractual', models.DateField(verbose_name='fin contractual', null=True)),
                ('fin_contractual_con_ampliaciones', models.DateField(verbose_name='fin contractual con ampliaciones', null=True)),
                ('obra', models.OneToOneField(verbose_name='info de obra', null=True, related_name='info_obra', to='core.Obras')),
            ],
            options={
                'verbose_name': 'info de obra',
                'verbose_name_plural': 'info de obras',
            },
        ),
    ]
