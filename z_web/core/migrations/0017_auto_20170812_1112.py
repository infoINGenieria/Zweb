# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizacion', '0001_initial'),
        ('core', '0016_auto_20170907_2359'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserExtension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('unidad_negocio', models.ForeignKey(verbose_name='unidad de negocio', null=True, to='organizacion.UnidadNegocio')),
                ('user', models.OneToOneField(related_name='extension', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='obras',
            name='unidad_negocio',
            field=models.ForeignKey(verbose_name='unidad de negocio', null=True, to='organizacion.UnidadNegocio'),
        ),
    ]
