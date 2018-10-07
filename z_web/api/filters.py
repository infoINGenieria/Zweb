import django_filters
from django.db import models
from django.db.models import Q

from equipos.models import (
    ParametrosGenerales, AsistenciaEquipo, RegistroAsistenciaEquipo, LubricantesValores,
    TrenRodajeValores, PosesionValores)
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
    estado = django_filters.CharFilter(method='estado_filter')
    excluir_costos_taller = django_filters.CharFilter(method='excluir_costos_taller_filter')

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

    class Meta:
        model = Equipos
        fields = (
            'n_interno', 'equipo', 'marca', 'modelo', 'año', 'dominio',
            'familia_equipo', 'estado', 'excluir_costos_taller'
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
