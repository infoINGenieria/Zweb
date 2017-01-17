# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametros', '0004_auto_20151127_1904'),
        ('core', '0014_auto_20160410_1234'),
        ('registro', '0022_auto_20160416_1304'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificacionInterna',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('monto', models.FloatField(verbose_name='Monto ($)')),
                ('obra', models.ForeignKey(related_name='certificaciones_internas_obras', to='core.Obras')),
                ('periodo', models.ForeignKey(related_name='certificaciones_internas_periodo', verbose_name='Periodo', to='parametros.Periodo')),
            ],
            options={
                'verbose_name_plural': 'certificaciones internas',
                'verbose_name': 'certificación interna',
            },
        ),
        migrations.AlterUniqueTogether(
            name='certificacioninterna',
            unique_together=set([('periodo', 'obra')]),
        ),
    ]
