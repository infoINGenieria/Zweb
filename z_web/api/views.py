# coding: utf-8
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed, ValidationError, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet, ModelViewSet

from api.serializers import (
    PresupuestoSerializer, RevisionSerializer, CostoTipoSerializer,
    ItemPresupuestoSerializer, ObrasSerializer, CertificacionProyeccionSerializer,
    CertificacionRealSerializer, CertificacionItemSerializer, PeriodoSerializer)
from api.filters import PresupuestoFilter, CertificacionFilter
from core.models import Obras, UserExtension
from costos.models import CostoTipo
from parametros.models import Periodo
from presupuestos.models import (
    Presupuesto, Revision, ItemPresupuesto)
from zweb_utils.views import generate_menu_user
from registro.models import CertificacionProyeccion, CertificacionReal, Certificacion
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


class TCCertficacionGraphView(AuthView):
    def get(self, request, *args, **kwargs):
        unidad_negocio = get_object_or_404(UnidadNegocio, codigo=self.kwargs.get('un'))
        obra = get_object_or_404(Obras, pk=self.kwargs.get('obra_pk'),
                                 unidad_negocio=unidad_negocio)
        data_graph = get_certificacion_graph(obra)
        return Response(data_graph)


class TCCostoGraphView(AuthView):
    def get(self, request, *args, **kwargs):
        unidad_negocio = get_object_or_404(UnidadNegocio, codigo=self.kwargs.get('un'))
        obra = get_object_or_404(Obras, pk=self.kwargs.get('obra_pk'),
                                 unidad_negocio=unidad_negocio)
        data_graph = get_costos_graph(obra)
        return Response(data_graph)


class TCAvanceGraphView(AuthView):
    def get(self, request, *args, **kwargs):
        unidad_negocio = get_object_or_404(UnidadNegocio, codigo=self.kwargs.get('un'))
        obra = get_object_or_404(Obras, pk=self.kwargs.get('obra_pk'),
                                 unidad_negocio=unidad_negocio)
        data_graph = get_avances_graph(obra)
        return Response(data_graph)


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


class TCConsolidadoGraphView(AuthView):
    def get(self, request, *args, **kwargs):
        unidad_negocio = get_object_or_404(UnidadNegocio, codigo=self.kwargs.get('un'))
        obra = get_object_or_404(Obras, pk=self.kwargs.get('obra_pk'),
                                 unidad_negocio=unidad_negocio)
        data_graph = get_consolidado_graph(obra)
        return Response(data_graph)


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
        qs = Presupuesto.objects.all()
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
    serializer_class = CertificacionRealSerializer
    filter_class = CertificacionFilter

    def get_queryset(self):
        obra_qs = self.get_centros_costos()
        return CertificacionReal.objects.filter(obra__in=obra_qs).order_by('-periodo__fecha_fin')


class CertificacionProyeccionViewSet(ModelViewSet, AuthView):
    serializer_class = CertificacionProyeccionSerializer
    filter_class = CertificacionFilter

    def get_queryset(self):
        obra_qs = self.get_centros_costos()
        return CertificacionProyeccion.objects.filter(obra__in=obra_qs).order_by('-periodo__fecha_fin')


class PeriodoViewSet(ModelViewSet, AuthView):
    serializer_class = PeriodoSerializer
    queryset = Periodo.objects.all().order_by('-fecha_fin')
