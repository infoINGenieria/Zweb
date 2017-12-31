# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrar_proyeccion_certificacion(apps, schema_editor):
    ProyeccionCertificacion = apps.get_model("proyecciones.ProyeccionCertificacion")
    ItemProyeccionCertificacion = apps.get_model("proyecciones.ItemProyeccionCertificacion")
    Certificacion = apps.get_model('registro.Certificacion')
    Obras = apps.get_model("core.Obras")

    ccs = Certificacion.objects.filter(
        es_proyeccion=True).values('obra').distinct()
    for cc in Obras.objects.filter(pk__in=ccs):
        periodo = Certificacion.objects.filter(
            es_proyeccion=True, obra=cc).order_by(
                "-periodo__fecha_fin").first().periodo
        proyeccion = ProyeccionCertificacion.objects.create(
            centro_costo=cc,
            periodo=periodo,
            es_base=True,
            base_numero=0
        )
        for item in Certificacion.objects.filter(obra=cc, es_proyeccion=True):
            monto = sum(item.items.values_list('monto', flat=True))
            ItemProyeccionCertificacion.objects.create(
                proyeccion=proyeccion,
                periodo=item.periodo,
                monto=monto
            )
        Certificacion.objects.filter(obra=cc, es_proyeccion=True).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('proyecciones', '0003_auto_20171231_0950'),
        ('registro', '0036_auto_20171216_1236'),
    ]

    operations = [
        migrations.RunPython(migrar_proyeccion_certificacion, migrations.RunPython.noop)
    ]
