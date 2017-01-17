# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def move_certificacion(apps, schema_editor):
    ServicioPrestadoUN = apps.get_model("costos", "ServicioPrestadoUN")
    CertificacionesInternas = apps.get_model("registro", "CertificacionInterna")
    for serv in ServicioPrestadoUN.objects.all():
        ci = CertificacionesInternas(
            periodo=serv.periodo,
            obra=serv.obra,
            monto=serv.monto
        )
        ci.save()


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0023_auto_20160416_2043'),
    ]

    operations = [
        migrations.RunPython(move_certificacion)
    ]
