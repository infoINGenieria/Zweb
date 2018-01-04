# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0037_delete_certificacionproyeccion'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CertificacionReal',
        ),
    ]
