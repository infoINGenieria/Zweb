# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def crear_item_certificaciones(apps, schema_editor):
    Certificacion = apps.get_model('registro.Certificacion')
    CertificacionItem = apps.get_model('registro.CertificacionItem')

    for cert in Certificacion.objects.all():
        item = CertificacionItem.objects.create(
            certificacion=cert,
            descripcion="{} - {} ({})".format(cert.obra.codigo, cert.obra.obra, cert.periodo.descripcion),
            monto=cert.monto
        )
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0029_certificacionitem'),
    ]

    operations = [
        migrations.RunPython(crear_item_certificaciones, migrations.RunPython.noop)
    ]
