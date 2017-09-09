# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20170117_1854'),
    ]

    operations = [
        migrations.CreateModel(
            name='CCT',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('nombre', models.CharField(verbose_name='nombre', max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'CCT',
                'verbose_name_plural': 'CCTs',
            },
        ),
        migrations.AddField(
            model_name='operarios',
            name='cct',
            field=models.ForeignKey(verbose_name='CCT', null=True, related_name='operarios', to='core.CCT'),
        ),
    ]
