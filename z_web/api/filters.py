import django_filters

from presupuestos.models import Presupuesto
from registro.models import Certificacion
from costos.models import AvanceObra
from proyecciones.models import ProyeccionAvanceObra, ProyeccionCertificacion


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
