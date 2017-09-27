# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presupuestos', '0002_auto_20170921_0829'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='revision',
            unique_together=set([('presupuesto', 'version')]),
        ),
    ]
