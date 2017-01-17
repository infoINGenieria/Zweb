# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20160410_1231'),
    ]

    operations = [
        migrations.RenameField('obras', 'prorratea_combustible', 'prorratea_costos')
    ]
