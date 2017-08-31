# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


def crear_unidad_negocio_y_asociar(apps, schema_editor):
    UnidadNegocio = apps.get_model('organizacion.UnidadNegocio')
    ms, _ = UnidadNegocio.objects.get_or_create(codigo='MS', nombre='Movimiento de Suelo')
    os, _ = UnidadNegocio.objects.get_or_create(codigo='OS', nombre='Obras de superficie')

    User = apps.get_model(settings.AUTH_USER_MODEL)
    Extension = apps.get_model('core.UserExtension')
    for user in User.objects.all():
        ext = Extension(user=user)
        if not user.is_superuser:
            ext.unidad_negocio = ms
        ext.save()

    Obras = apps.get_model('core.Obras')
    Obras.objects.update(unidad_negocio=ms)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20170812_1112'),
    ]

    operations = [
        migrations.RunPython(crear_unidad_negocio_y_asociar, migrations.RunPython.noop)
    ]
