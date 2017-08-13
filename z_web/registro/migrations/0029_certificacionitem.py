# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0028_auto_20170126_2106'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificacionItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('descripcion', models.CharField(verbose_name='descripción', max_length=255)),
                ('monto', models.DecimalField(verbose_name='Monto ($)', max_digits=18, decimal_places=2)),
                ('adicional', models.BooleanField(verbose_name='adicional', default=False)),
                ('certificacion', models.ForeignKey(verbose_name='certificación', related_name='items', to='registro.Certificacion')),
            ],
            options={
                'verbose_name': 'ítem certificación',
                'verbose_name_plural': 'ítemes de certificaciones',
            },
        ),
    ]
