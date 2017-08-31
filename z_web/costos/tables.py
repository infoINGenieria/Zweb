# coding=utf-8
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse_lazy

from django_tables2 import A, URLColumn, BooleanColumn, Column

from zweb_utils.tables_filters import DefaultTable
from .models import Costo


class CostoBaseTable(DefaultTable):
    links_action = Column(verbose_name='Acciones', empty_values=())

    def render_links_action(self, record):
        return mark_safe(
            '<a class="btn btn-danger btn-xs pull-right" data-toggle="modal" data-target="#modal"'
            ' data-tooltip href="{}"><i class="fa fa-trash"></i> Eliminar</a> '
            '<a class="btn btn-primary btn-xs pull-right" data-toggle="modal" data-target="#modal"'
            ' data-tooltip href="{}"><i class="fa fa-edit"></i> Modificar</a> '
            ''.format(
                reverse_lazy('costos:costos_delete', args=(record.pk, )),
                reverse_lazy('costos:costos_edit', args=(record.pk, ))
            )
        )

    class Meta(DefaultTable.Meta):
        model = Costo
        fields = ('links_action', )


class CostosByCCTotalTable(CostoBaseTable):

    class Meta(CostoBaseTable.Meta):
        fields = ('periodo', 'centro_costo', 'observacion', 'monto_total', ) + CostoBaseTable.Meta.fields


class CostosByCCMontoHSTable(CostoBaseTable):

    class Meta(CostoBaseTable.Meta):
        fields = ('periodo', 'centro_costo', 'observacion', 'monto_hora', 'monto_mes', 'monto_anio') + CostoBaseTable.Meta.fields


class CostosByEquipoMontoHSTable(CostoBaseTable):

    class Meta(CostoBaseTable.Meta):
        fields = ('periodo', 'familia_equipo', 'observacion', 'monto_hora', 'monto_mes', 'monto_anio') + CostoBaseTable.Meta.fields


class CostosByEquipoTotalTable(CostoBaseTable):

    class Meta(CostoBaseTable.Meta):
        fields = ('periodo', 'familia_equipo', 'observacion', 'monto_total', ) + CostoBaseTable.Meta.fields
