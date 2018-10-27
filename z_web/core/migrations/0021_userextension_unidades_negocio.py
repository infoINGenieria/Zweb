# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def add_negocio(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    for user in User.objects.all():
        try:
            if user.extension.unidad_negocio:
                un = user.extension.unidad_negocio
                user.extension.unidades_negocio.add(un)
                user.extension.save()
        except:
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('organizacion', '0002_auto_20170922_0824'),
        ('core', '0020_infoobra'),
    ]

    operations = [
        migrations.AddField(
            model_name='userextension',
            name='unidades_negocio',
            field=models.ManyToManyField(verbose_name='unidades de negocio', related_name='unidades_de_negocio', to='organizacion.UnidadNegocio'),
        ),
        migrations.RunPython(add_negocio, migrations.RunPython.noop)
    ]
