# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrar_proyeccion_avance(apps, schema_editor):
    ProyeccionAvanceObra = apps.get_model("proyecciones.ProyeccionAvanceObra")
    ItemProyeccionAvanceObra = apps.get_model("proyecciones.ItemProyeccionAvanceObra")
    AvanceObra = apps.get_model('costos.AvanceObra')
    Obras = apps.get_model("core.Obras")

    ccs = AvanceObra.objects.filter(es_proyeccion=True).values('centro_costo').distinct()
    for cc in Obras.objects.filter(pk__in=ccs):
        periodo = AvanceObra.objects.filter(
            es_proyeccion=True, centro_costo=cc).order_by(
                "-periodo__fecha_fin").first().periodo
        proyeccion = ProyeccionAvanceObra.objects.create(
            centro_costo=cc,
            periodo=periodo,
            es_base=True,
            base_numero=0
        )
        for item in AvanceObra.objects.filter(centro_costo=cc, es_proyeccion=True):
            ItemProyeccionAvanceObra.objects.create(
                proyeccion=proyeccion,
                periodo=item.periodo,
                avance=item.avance
            )
        AvanceObra.objects.filter(centro_costo=cc, es_proyeccion=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('proyecciones', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrar_proyeccion_avance, migrations.RunPython.noop)
    ]
