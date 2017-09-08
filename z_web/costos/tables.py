# coding=utf-8
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse_lazy

from django_tables2 import A, URLColumn, BooleanColumn, Column

from zweb_utils.tables_filters import DefaultTable
from .models import CostoReal, CostoProyeccion


class CostoBaseTable(DefaultTable):
    links_action = Column(verbose_name='Acciones', empty_values=())

    delete_link = 'costos:costos_delete'
    edit_link = 'costos:costos_edit'

    def render_links_action(self, record):
        return mark_safe(
            '<a class="btn btn-danger btn-xs pull-right" data-toggle="modal" data-target="#modal"'
            ' data-tooltip href="{}"><i class="fa fa-trash"></i> Eliminar</a> '
            '<a class="btn btn-primary btn-xs pull-right" data-toggle="modal" data-target="#modal"'
            ' data-tooltip href="{}"><i class="fa fa-edit"></i> Modificar</a> '
            ''.format(
                reverse_lazy(self.delete_link, args=(record.pk, )),
                reverse_lazy(self.edit_link, args=(record.pk, ))
            )
        )



class CostoTableGeneric(CostoBaseTable):

    class Meta(CostoBaseTable.Meta):
        model = CostoReal
        fields = ('periodo', 'tipo_costo', 'centro_costo', 'familia_equipo', 'observacion',
                  'monto_total', 'monto_hora', 'links_action')


class CostosByCCTotalTable(CostoBaseTable):

    class Meta(CostoBaseTable.Meta):
        model = CostoReal
        fields = ('periodo', 'tipo_costo', 'centro_costo', 'observacion',
                  'monto_total', 'links_action')


class CostosByEquipoMontoHSTable(CostoBaseTable):

    class Meta(CostoBaseTable.Meta):
        model = CostoReal
        fields = ('periodo', 'tipo_costo', 'familia_equipo', 'observacion',
                  'monto_hora', 'monto_mes', 'monto_anio', 'links_action')


#################
# Proyecciones  #
#################

class ProyeccionBaseTable(CostoBaseTable):
    delete_link = 'costos:proyecciones_delete'
    edit_link = 'costos:proyecciones_edit'


class ProyeccionTableGeneric(ProyeccionBaseTable):
    class Meta(ProyeccionBaseTable.Meta):
        model = CostoProyeccion
        fields = ('periodo', 'tipo_costo', 'centro_costo', 'familia_equipo', 'observacion',
                  'monto_total', 'monto_hora', 'links_action')


class ProyeccionByCCTotalTable(ProyeccionBaseTable):
    class Meta(ProyeccionBaseTable.Meta):
        model = CostoProyeccion
        fields = ('periodo', 'tipo_costo', 'centro_costo', 'observacion',
                  'monto_total', 'links_action')


class ProyeccionByEquipoMontoHSTable(ProyeccionBaseTable):
    class Meta(ProyeccionBaseTable.Meta):
        model = CostoProyeccion
        fields = ('periodo', 'tipo_costo', 'familia_equipo', 'observacion',
                  'monto_hora', 'monto_mes', 'monto_anio', 'links_action')

