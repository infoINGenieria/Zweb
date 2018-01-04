# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0036_auto_20171216_1236'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CertificacionProyeccion',
        ),
    ]
