# coding: utf-8
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Max, Min

from rest_framework import status
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import MethodNotAllowed, ValidationError, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet, ModelViewSet

from api.serializers import (
    PresupuestoSerializer, RevisionSerializer, CostoTipoSerializer,
    ItemPresupuestoSerializer, ObrasSerializer,
    CertificacionSerializer, CertificacionItemSerializer, PeriodoSerializer,
    AvanceObraSerializer, ProyeccionAvanceObraSerializer,
    ProyeccionCertificacionSerializer, ProyeccionCostoSerializer)
from api.filters import (
    PresupuestoFilter, CertificacionFilter, AvanceObraFilter,
    ProyeccionAvanceObraFilter, ProyeccionCertificacionFilter,
    ProyeccionCostoFilter)
from core.models import Obras, UserExtension
from costos.models import CostoTipo, AvanceObra, Costo
from parametros.models import Periodo
from presupuestos.models import (
    Presupuesto, Revision, ItemPresupuesto)
from proyecciones.models import (
    ProyeccionAvanceObra, ProyeccionCertificacion, ProyeccionCosto)
from zweb_utils.views import generate_menu_user
from registro.models import Certificacion
from organizacion.models import UnidadNegocio
from frontend.tablero.os import (
    generar_tabla_tablero, get_certificacion_graph, get_costos_graph,
    get_avances_graph, get_consolidado_graph)


class AuthView(APIView):
    """
    Base class to endpoint views.
    """
    permission_classes = (IsAuthenticated, )

    def get_centros_costos(self):
        obra_qs = Obras.get_centro_costos(self.request.user)
        return obra_qs


class DynamicMenuView(APIView):
    def get(self, request, *args, **kwargs):
        menu = generate_menu_user(request.user)
        return Response(menu)


class GraphDataMixin(object):

    def get_data(self, obra, periodo):
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        unidad_negocio = get_object_or_404(UnidadNegocio, codigo=self.kwargs.get('un'))
        obra = get_object_or_404(Obras, pk=self.kwargs.get('obra_pk'),
                                 unidad_negocio=unidad_negocio)
        periodo = get_object_or_404(Periodo, pk=self.kwargs.get('periodo_pk'))
        try:
            data_graph = self.get_data(obra, periodo)
        except Exception as e:
            raise ParseError(e)
        return Response(data_graph)


class TCCertficacionGraphView(GraphDataMixin, AuthView):
    def get_data(self, obra, periodo):
        return get_certificacion_graph(obra, periodo)


class TCCostoGraphView(GraphDataMixin, AuthView):

    def get_data(self, obra, periodo):
        return get_costos_graph(obra, periodo)


class TCAvanceGraphView(GraphDataMixin, AuthView):
    def get_data(self, obra, periodo):
        return get_avances_graph(obra, periodo)


class TCConsolidadoGraphView(GraphDataMixin, AuthView):
    def get_data(self, obra, periodo):
        return get_consolidado_graph(obra, periodo)


class TableroControTablalView(AuthView):
    def get(self, request, *args, **kwargs):
        unidad_negocio = get_object_or_404(UnidadNegocio, codigo=self.kwargs.get('un'))
        obra = get_object_or_404(Obras, pk=self.kwargs.get('obra_pk'),
                                 unidad_negocio=unidad_negocio)
        periodo = get_object_or_404(Periodo, pk=self.kwargs.get('periodo_pk'))
        try:
            data_tablero = generar_tabla_tablero(obra, periodo)
        except Exception as e:
            raise ParseError(e)
        return Response(data_tablero)


class PresupuestoRelatedMixin(object):
    """
    Este mixin obtiene el id de presupuesto de la url.
    Usar en endpoint anidados a presupuesto
    """

    def initial(self, request, *args, **kwargs):
        presupuesto_pk = self.kwargs.get('presupuesto_pk')
        try:
            self.presupuesto = Presupuesto.objects.get(pk=presupuesto_pk)
        except Presupuesto.DoesNotExist:
            raise Http404
        return super(PresupuestoRelatedMixin, self).initial(request, *args, **kwargs)

    def get_serializer_context(self):
        """
        Poner el presupuesto en el contexto del serializer
        """
        return {'presupuesto_pk': self.kwargs["presupuesto_pk"]}


class PresupuestoViewSet(ModelViewSet, AuthView):
    serializer_class = PresupuestoSerializer
    filter_class = PresupuestoFilter

    def get_queryset(self):
        qs = Presupuesto.objects.filter(centro_costo__in=self.get_centros_costos())
        return qs


class RevisionViewSet(PresupuestoRelatedMixin, ModelViewSet, AuthView):
    serializer_class = RevisionSerializer

    def get_queryset(self):
        qs = Revision.objects.filter(presupuesto=self.presupuesto)
        return qs.order_by('-version')

    def perform_create(self, serializer):
        serializer.save(presupuesto=self.presupuesto)

    def get_object(self):
        try:
            return Revision.objects.get(
                presupuesto=self.presupuesto,
                version=self.kwargs.get('pk'))
        except Revision.DoesNotExist:
            raise Http404


class ItemPresupuestoViewSet(PresupuestoRelatedMixin, ModelViewSet, AuthView):
    serializer_class = ItemPresupuestoSerializer

    def initial(self, request, *args, **kwargs):
        _super = super(ItemPresupuestoViewSet, self).initial(request, *args, **kwargs)
        version = self.kwargs.get('version')
        try:
            self.revision = Revision.objects.get(presupuesto=self.presupuesto, version=version)
        except Revision.DoesNotExist:
            raise Http404
        return _super

    def get_queryset(self):
        return ItemPresupuesto.objects.filter(revision=self.revision)

    def perform_create(self, serializer):
        serializer.save(revision=self.revision)


class TipoCostoViewSet(ModelViewSet, AuthView):
    serializer_class = CostoTipoSerializer
    queryset = CostoTipo.objects.filter(relacionado_con='cc', unidad_monto='total')

    def destroy(self, *args, **kwargs):
        obj = self.get_object()
        if ItemPresupuesto.objects.filter(tipo=obj).exists():
            raise ParseError("Hay presupuestos utilizando este Tipo de "
                             "ítem de presupuesto. No se puede eliminar.")
        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CentroCostoViewSet(ModelViewSet, AuthView):
    serializer_class = ObrasSerializer

    def get_queryset(self):
        return self.get_centros_costos()


class CertificacionRealViewSet(ModelViewSet, AuthView):
    serializer_class = CertificacionSerializer
    filter_class = CertificacionFilter

    def get_queryset(self):
        obra_qs = self.get_centros_costos()
        return Certificacion.objects.filter(obra__in=obra_qs).order_by('-periodo__fecha_fin')


class PeriodoViewSet(ModelViewSet, AuthView):
    serializer_class = PeriodoSerializer
    queryset = Periodo.objects.all().order_by('-fecha_fin')


class AvanceObraViewSet(ModelViewSet, AuthView):
    serializer_class = AvanceObraSerializer
    filter_class = AvanceObraFilter

    def get_queryset(self):
        obra_qs = self.get_centros_costos()
        return AvanceObra.objects.filter(
            centro_costo__in=obra_qs).order_by('periodo__fecha_fin')


class ProyeccionAvanceObraViewSet(ModelViewSet, AuthView):
    serializer_class = ProyeccionAvanceObraSerializer
    filter_class = ProyeccionAvanceObraFilter

    def get_queryset(self):
        obra_qs = self.get_centros_costos()
        return ProyeccionAvanceObra.objects.filter(
            centro_costo__in=obra_qs).order_by('periodo__fecha_fin')

    @detail_route(methods=['post'], url_path='hacer-vigente')
    def hacer_vigente(self, request, **kwargs):
        pao = self.get_object()
        last = ProyeccionAvanceObra.objects.filter(
            centro_costo=pao.centro_costo,
            es_base=True).aggregate(last=Max("base_numero"))
        pao.es_base = True
        pao.base_numero = 0
        if last.get("last") != None:
            pao.base_numero = last.get("last") + 1
        pao.save()
        return Response(ProyeccionAvanceObraSerializer(pao).data)


class ProyeccionCertificacionViewSet(ModelViewSet, AuthView):
    serializer_class = ProyeccionCertificacionSerializer
    filter_class = ProyeccionCertificacionFilter

    def get_queryset(self):
        obra_qs = self.get_centros_costos()
        return ProyeccionCertificacion.objects.filter(
            centro_costo__in=obra_qs).order_by('periodo__fecha_fin')

    @detail_route(methods=['post'], url_path='hacer-vigente')
    def hacer_vigente(self, request, **kwargs):
        pao = self.get_object()
        last = ProyeccionCertificacion.objects.filter(
            centro_costo=pao.centro_costo,
            es_base=True).aggregate(last=Max("base_numero"))
        pao.es_base = True
        pao.base_numero = 0
        if last.get("last") != None:
            pao.base_numero = last.get("last") + 1
        pao.save()
        return Response(ProyeccionCertificacionSerializer(pao).data)


class ProyeccionCostoViewSet(ModelViewSet, AuthView):
    serializer_class = ProyeccionCostoSerializer
    filter_class = ProyeccionCostoFilter

    def get_queryset(self):
        obra_qs = self.get_centros_costos()
        return ProyeccionCosto.objects.filter(
            centro_costo__in=obra_qs).order_by('periodo__fecha_fin')

    @detail_route(methods=['post'], url_path='hacer-vigente')
    def hacer_vigente(self, request, **kwargs):
        pao = self.get_object()
        last = ProyeccionCosto.objects.filter(
            centro_costo=pao.centro_costo,
            es_base=True).aggregate(last=Max("base_numero"))
        pao.es_base = True
        pao.base_numero = 0
        if last.get("last") != None:
            pao.base_numero = last.get("last") + 1
        pao.save()
        return Response(ProyeccionCostoSerializer(pao).data)
