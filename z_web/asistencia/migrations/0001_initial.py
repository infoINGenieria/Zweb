# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizacion', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asistencia',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('fecha', models.DateField(verbose_name='Fecha de presentismo')),
                ('nombre_responsable', models.CharField(help_text='Se completará automaticamente con el responsable del proyecto seleccionado', verbose_name='Nombre del responsable', max_length=255)),
                ('nombre_proyecto', models.CharField(help_text='Se completará automaticamente con el nombre del proyecto seleccionado.', verbose_name='Nombre del proyecto', max_length=255)),
                ('proyecto', models.ForeignKey(related_name='asistencias', to='organizacion.Proyecto')),
            ],
            options={
                'verbose_name_plural': 'asistencias',
                'verbose_name': 'asistencia',
            },
        ),
        migrations.CreateModel(
            name='EstadoAsistencia',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('situacion', models.CharField(verbose_name='situación', max_length=255)),
                ('codigo', models.CharField(unique=True, verbose_name='código', max_length=5)),
                ('observaciones', models.CharField(null=True, verbose_name='observaciones', max_length=255, blank=True)),
                ('no_ocioso', models.BooleanField(help_text='Seleccione esta opción para indicar que el estado no implica ociosidad por parte del empleado', default=False, verbose_name='No está ocioso')),
                ('activo', models.BooleanField(default=True, verbose_name='activo')),
            ],
            options={
                'verbose_name_plural': 'estados de asistencias',
                'verbose_name': 'estado de asistencia',
                'ordering': ('situacion',),
            },
        ),
        migrations.CreateModel(
            name='HistoricalAsistencia',
            fields=[
                ('id', models.IntegerField(db_index=True, verbose_name='ID', auto_created=True, blank=True)),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Fecha de creación', blank=True)),
                ('modified_at', models.DateTimeField(editable=False, verbose_name='Fecha de modificación', blank=True)),
                ('fecha', models.DateField(verbose_name='Fecha de presentismo')),
                ('nombre_responsable', models.CharField(help_text='Se completará automaticamente con el responsable del proyecto seleccionado', verbose_name='Nombre del responsable', max_length=255)),
                ('nombre_proyecto', models.CharField(help_text='Se completará automaticamente con el nombre del proyecto seleccionado.', verbose_name='Nombre del proyecto', max_length=255)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('proyecto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', blank=True, to='organizacion.Proyecto', db_constraint=False)),
            ],
            options={
                'get_latest_by': 'history_date',
                'verbose_name': 'historical asistencia',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
        migrations.CreateModel(
            name='HistoricalEstadoAsistencia',
            fields=[
                ('id', models.IntegerField(db_index=True, verbose_name='ID', auto_created=True, blank=True)),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Fecha de creación', blank=True)),
                ('modified_at', models.DateTimeField(editable=False, verbose_name='Fecha de modificación', blank=True)),
                ('situacion', models.CharField(verbose_name='situación', max_length=255)),
                ('codigo', models.CharField(db_index=True, verbose_name='código', max_length=5)),
                ('observaciones', models.CharField(null=True, verbose_name='observaciones', max_length=255, blank=True)),
                ('no_ocioso', models.BooleanField(help_text='Seleccione esta opción para indicar que el estado no implica ociosidad por parte del empleado', default=False, verbose_name='No está ocioso')),
                ('activo', models.BooleanField(default=True, verbose_name='activo')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'history_date',
                'verbose_name': 'historical estado de asistencia',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
        migrations.CreateModel(
            name='HistoricalRegistroAsistencia',
            fields=[
                ('id', models.IntegerField(db_index=True, verbose_name='ID', auto_created=True, blank=True)),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Fecha de creación', blank=True)),
                ('modified_at', models.DateTimeField(editable=False, verbose_name='Fecha de modificación', blank=True)),
                ('codigo_estado', models.CharField(help_text='Se establecerá automaticamente con el código del estado seleccionado.', verbose_name='Código', max_length=5)),
                ('observaciones', models.CharField(null=True, verbose_name='observaciones', max_length=255, blank=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('asistencia', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', blank=True, to='asistencia.Asistencia', db_constraint=False)),
                ('estado', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', blank=True, to='asistencia.EstadoAsistencia', db_constraint=False)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('persona', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', blank=True, to='organizacion.Persona', db_constraint=False)),
            ],
            options={
                'get_latest_by': 'history_date',
                'verbose_name': 'historical registro de asistencia',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
        migrations.CreateModel(
            name='HistoricalResponsableAsistencia',
            fields=[
                ('id', models.IntegerField(db_index=True, verbose_name='ID', auto_created=True, blank=True)),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Fecha de creación', blank=True)),
                ('modified_at', models.DateTimeField(editable=False, verbose_name='Fecha de modificación', blank=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('persona', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', blank=True, to='organizacion.Persona', db_constraint=False)),
                ('proyecto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', blank=True, to='organizacion.Proyecto', db_constraint=False)),
            ],
            options={
                'get_latest_by': 'history_date',
                'verbose_name': 'historical responsable',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
        migrations.CreateModel(
            name='MovimientoPersona',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('situacion', models.SmallIntegerField(default=1, verbose_name='situacion', choices=[(1, 'ALTA'), (2, 'BAJA')])),
                ('fechahora', models.DateTimeField(verbose_name='fecha y hora')),
                ('persona', models.ForeignKey(to='organizacion.Persona')),
                ('usuario', models.ForeignKey(null=True, verbose_name='realizado por', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'verbose_name_plural': 'movimiento de personas',
                'verbose_name': 'movimiento de persona',
            },
        ),
        migrations.CreateModel(
            name='RegistroAsistencia',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('codigo_estado', models.CharField(help_text='Se establecerá automaticamente con el código del estado seleccionado.', verbose_name='Código', max_length=5)),
                ('observaciones', models.CharField(null=True, verbose_name='observaciones', max_length=255, blank=True)),
                ('asistencia', models.ForeignKey(related_name='items', to='asistencia.Asistencia')),
                ('estado', models.ForeignKey(default=6, verbose_name='estado de presentismo', to='asistencia.EstadoAsistencia')),
                ('persona', models.ForeignKey(related_name='registro_asistencia', to='organizacion.Persona')),
            ],
            options={
                'verbose_name_plural': 'registros de asistencia',
                'verbose_name': 'registro de asistencia',
            },
        ),
        migrations.CreateModel(
            name='ResponsableAsistencia',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('persona', models.ForeignKey(null=True, verbose_name='persona', related_name='responsable_rel', to='organizacion.Persona')),
                ('proyecto', models.OneToOneField(null=True, verbose_name='proyecto', related_name='responsable_rel', to='organizacion.Proyecto')),
            ],
            options={
                'verbose_name_plural': 'responsables',
                'verbose_name': 'responsable',
            },
        ),
        migrations.AddField(
            model_name='historicalasistencia',
            name='responsable',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', blank=True, to='asistencia.ResponsableAsistencia', db_constraint=False),
        ),
        migrations.AddField(
            model_name='asistencia',
            name='responsable',
            field=models.ForeignKey(null=True, related_name='mis_asistencias', to='asistencia.ResponsableAsistencia'),
        ),
        migrations.AlterUniqueTogether(
            name='responsableasistencia',
            unique_together=set([('persona', 'proyecto')]),
        ),
        migrations.AlterUniqueTogether(
            name='registroasistencia',
            unique_together=set([('asistencia', 'persona')]),
        ),
        migrations.AlterUniqueTogether(
            name='asistencia',
            unique_together=set([('fecha', 'proyecto')]),
        ),
    ]
