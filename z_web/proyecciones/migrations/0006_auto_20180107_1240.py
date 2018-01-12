# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrar_proyeccion_costos(apps, schema_editor):
    ProyeccionCosto = apps.get_model("proyecciones.ProyeccionCosto")
    ItemProyeccionCosto = apps.get_model("proyecciones.ItemProyeccionCosto")
    Costo = apps.get_model('costos.Costo')
    Obras = apps.get_model("core.Obras")

    ccs = Costo.objects.filter(
        es_proyeccion=True).values('centro_costo').distinct()
    for cc in Obras.objects.filter(pk__in=ccs):
        periodo = Costo.objects.filter(
            es_proyeccion=True, centro_costo=cc).order_by(
                "-periodo__fecha_fin").first().periodo
        proyeccion = ProyeccionCosto.objects.create(
            centro_costo=cc,
            periodo=periodo,
            es_base=True,
            base_numero=0
        )
        for item in Costo.objects.filter(centro_costo=cc, es_proyeccion=True):
            ItemProyeccionCosto.objects.create(
                proyeccion=proyeccion,
                periodo=item.periodo,
                tipo_costo=item.tipo_costo,
                monto=item.monto_total
            )
        c = Costo.objects.filter(centro_costo=cc, es_proyeccion=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('proyecciones', '0005_auto_20180104_2152'),
    ]

    operations = [
        migrations.RunPython(migrar_proyeccion_costos, migrations.RunPython.noop)
    ]
