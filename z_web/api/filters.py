import django_filters
from django.db import models
from django.db.models import Q

from equipos.models import (
    ParametrosGenerales, AsistenciaEquipo, RegistroAsistenciaEquipo, LubricantesValores,
    TrenRodajeValores, PosesionValores, ReparacionesValores,
    EquipoAlquiladoValores, ManoObraValores, CostoEquipoValores)
from core.models import Equipos
from presupuestos.models import Presupuesto
from registro.models import Certificacion
from costos.models import AvanceObra
from proyecciones.models import (
    ProyeccionAvanceObra, ProyeccionCertificacion,
    ProyeccionCosto)


class PresupuestoFilter(django_filters.FilterSet):
    desde = django_filters.DateFilter(name="fecha", lookup_expr='gte')
    hasta = django_filters.DateFilter(name="fecha", lookup_expr='lte')

    class Meta:
        model = Presupuesto
        fields = ('centro_costo', 'desde', 'hasta')


class CertificacionFilter(django_filters.FilterSet):
    class Meta:
        model = Certificacion
        fields = ('obra', 'periodo')


class AvanceObraFilter(django_filters.FilterSet):

    class Meta:
        model = AvanceObra
        fields = ('centro_costo', 'periodo')


class ProyeccionAvanceObraFilter(django_filters.FilterSet):

    class Meta:
        model = ProyeccionAvanceObra
        fields = ('centro_costo', 'periodo')


class ProyeccionCertificacionFilter(django_filters.FilterSet):

    class Meta:
        model = ProyeccionCertificacion
        fields = ('centro_costo', 'periodo')


class ProyeccionCostoFilter(django_filters.FilterSet):

    class Meta:
        model = ProyeccionCosto
        fields = ('centro_costo', 'periodo')


class EquiposFilter(django_filters.FilterSet):
    equipo = django_filters.CharFilter(method='buscar_en_equipo')
    estado = django_filters.CharFilter(method='estado_filter')
    excluir_costos_taller = django_filters.CharFilter(method='excluir_costos_taller_filter')
    alquilado = django_filters.CharFilter(method='alquilado_filter')
    implica_mo_logistica = django_filters.CharFilter(method='implica_mo_logistica_filter')

    def excluir_costos_taller_filter(self, queryset, name, value):
        if value == '1':
            return queryset.filter(excluir_costos_taller=True)
        elif value == '0':
            return queryset.filter(excluir_costos_taller=False)
        return queryset

    def estado_filter(self, queryset, name, value):
        if value == '1':
            return queryset.filter(fecha_baja__isnull=True)
        elif value == '0':
            return queryset.filter(fecha_baja__isnull=False)
        return queryset

    def alquilado_filter(self, queryset, name, value):
        if value == '1':
            return queryset.filter(es_alquilado=True)
        elif value == '0':
            return queryset.filter(es_alquilado=False)
        return queryset

    def implica_mo_logistica_filter(self, queryset, name, value):
        if value == '1':
            return queryset.filter(implica_mo_logistica=True)
        elif value == '0':
            return queryset.filter(implica_mo_logistica=False)
        return queryset

    def buscar_en_equipo(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(n_interno__icontains=value) |
                Q(equipo__icontains=value) |
                Q(marca__icontains=value) |
                Q(modelo__icontains=value) |
                Q(dominio__icontains=value)
            ).distinct()
        return queryset

    class Meta:
        model = Equipos
        fields = (
            'equipo', 'estado', 'excluir_costos_taller', 'alquilado', 'implica_mo_logistica'
        )
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
         }


class ParametrosGeneralesFilter(django_filters.FilterSet):

    class Meta:
        model = ParametrosGenerales
        fields = ('valido_desde', )


class AsistenciaEquipoFilter(django_filters.FilterSet):
    desde = django_filters.DateFilter(name="dia", lookup_expr='gte')
    hasta = django_filters.DateFilter(name="dia", lookup_expr='lte')

    class Meta:
        model = AsistenciaEquipo
        fields = ('desde', 'hasta', )


class RegistroAsistenciaEquipoFilter(django_filters.FilterSet):

    class Meta:
        model = RegistroAsistenciaEquipo
        fields = ('equipo', 'centro_costo', )


class ValoresEquipoTallerFilter(django_filters.FilterSet):
    equipo = django_filters.CharFilter(method='buscar_en_equipo')

    def buscar_en_equipo(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(equipo__n_interno__icontains=value) |
                Q(equipo__equipo__icontains=value) |
                Q(equipo__marca__icontains=value) |
                Q(equipo__modelo__icontains=value) |
                Q(equipo__dominio__icontains=value)
            ).distinct()
        return queryset

    class Meta:
        model = LubricantesValores
        fields = ('equipo', 'valido_desde', )


class TrenRodajeValoresTallerFilter(ValoresEquipoTallerFilter):
    class Meta(ValoresEquipoTallerFilter.Meta):
        model = TrenRodajeValores


class PosesionValoresTallerFilter(ValoresEquipoTallerFilter):
    class Meta(ValoresEquipoTallerFilter.Meta):
        model = PosesionValores


class ReparacionesValoresTallerFilter(ValoresEquipoTallerFilter):
    class Meta(ValoresEquipoTallerFilter.Meta):
        model = ReparacionesValores


class EquipoAlquiladoValoresTallerFilter(ValoresEquipoTallerFilter):
    class Meta(ValoresEquipoTallerFilter.Meta):
        model = EquipoAlquiladoValores


class CostoEquipoValoresTallerFilter(ValoresEquipoTallerFilter):
    class Meta(ValoresEquipoTallerFilter.Meta):
        model = CostoEquipoValores


class ManoObraValoresTallerFilter(django_filters.FilterSet):
    class Meta:
        model = ManoObraValores
        fields = ('valido_desde', )
