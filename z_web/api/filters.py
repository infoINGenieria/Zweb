import django_filters
from django.db import models

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

    def estado_filter(self, queryset, name, value):
        if value == '1':
            return queryset.filter(fecha_baja__isnull=True)
        elif value == '0':
            return queryset.filter(fecha_baja__isnull=False)
        return queryset

    class Meta:
        model = Equipos
        fields = ('n_interno', 'equipo', 'marca', 'modelo', 'año', 'dominio', 'familia_equipo', 'estado')
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
         }
