# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import registro.models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_infoobra'),
        ('parametros', '0006_auto_20171122_2224'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('registro', '0038_delete_certificacionreal'),
    ]

    operations = [
        migrations.CreateModel(
            name='TableroControlOS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('pdf', models.FileField(verbose_name='PDF', upload_to=registro.models.get_path_images)),
                ('comentario', models.TextField(verbose_name='comentario', blank=True, null=True)),
                ('info_obra', jsonfield.fields.JSONField(verbose_name='info de obra')),
                ('revisiones_historico', jsonfield.fields.JSONField(verbose_name='historico de revisiones')),
                ('tablero_data', jsonfield.fields.JSONField(verbose_name='tabla del tablero')),
                ('consolidado_data', jsonfield.fields.JSONField(verbose_name='data del gráfico consolidado')),
                ('certificacion_data', jsonfield.fields.JSONField(verbose_name='data del gráfico de certificación')),
                ('costos_data', jsonfield.fields.JSONField(verbose_name='data del gráfico de costos')),
                ('avance_data', jsonfield.fields.JSONField(verbose_name='data del gráfico de avance de obra')),
                ('resultados_data', jsonfield.fields.JSONField(verbose_name='data del gráfico de resultados', blank=True, null=True)),
                ('tablero_html', models.TextField(null=True)),
                ('consolidado_img', models.ImageField(null=True, upload_to=registro.models.get_path_images)),
                ('certificacion_img', models.ImageField(null=True, upload_to=registro.models.get_path_images)),
                ('costos_img', models.ImageField(null=True, upload_to=registro.models.get_path_images)),
                ('avance_img', models.ImageField(null=True, upload_to=registro.models.get_path_images)),
                ('resultado_img', models.ImageField(null=True, upload_to=registro.models.get_path_images)),
                ('obra', models.ForeignKey(related_name='tc_emitidos', to='core.Obras')),
                ('periodo', models.ForeignKey(verbose_name='Periodo', related_name='tc_emitidos_by_periodo', to='parametros.Periodo')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'tablero de control',
                'verbose_name_plural': 'tableros de control',
            },
        ),
        migrations.AlterUniqueTogether(
            name='tablerocontrolos',
            unique_together=set([('periodo', 'obra')]),
        ),
    ]
