# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0031_remove_certificacion_monto'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificacionProyeccion',
            fields=[
            ],
            options={
                'verbose_name': 'proyección de certificación',
                'verbose_name_plural': 'proyecciones de certificación',
                'proxy': True,
            },
            bases=('registro.certificacion',),
        ),
        migrations.CreateModel(
            name='CertificacionReal',
            fields=[
            ],
            options={
                'verbose_name': 'certificación',
                'verbose_name_plural': 'certificaciones',
                'proxy': True,
            },
            bases=('registro.certificacion',),
        ),
        migrations.AddField(
            model_name='certificacion',
            name='es_proyeccion',
            field=models.BooleanField(verbose_name='Es una proyección', default=False),
        ),
    ]
