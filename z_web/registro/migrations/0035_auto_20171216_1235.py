# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def add_concepto_item_certificaciones(apps, schema_editor):
    CertificacionItem = apps.get_model('registro.CertificacionItem')
    CertificacionItem.objects.filter(adicional=True).update(concepto='cambios')


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0034_auto_20171216_1231'),
    ]

    operations = [
        migrations.RunPython(add_concepto_item_certificaciones, migrations.RunPython.noop)
    ]
