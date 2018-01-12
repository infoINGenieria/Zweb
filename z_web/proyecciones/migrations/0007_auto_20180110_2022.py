# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecciones', '0006_auto_20180107_1240'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='proyeccionavanceobra',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='proyeccioncertificacion',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='proyeccioncosto',
            unique_together=set([]),
        ),
    ]
