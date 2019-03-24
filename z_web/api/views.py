# coding: utf-8
import json
from decimal import Decimal as D

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Max, Min, Q
from django.db.transaction import atomic
from django.utils import timezone

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
    ProyeccionCertificacionSerializer, ProyeccionCostoSerializer,
    TableroControlOSSerializer, EquipoSerializer, FamiliaEquipoSerializer,
    ParametrosGeneralesTallerSerializer, AsistenciaEquipoSerializer,
    RegistroAsistenciaEquipoSerializer, ReportAsistenciaItemCCSerializer,
    TableroControlTallerSerializer, ValoresLubricantesTallerSerializer,
    ValoresTrenRodajeTallerSerializer, ValoresPosesionTallerSerializer,
    ValoresReparacionesTallerSerializer, ValoresManoObraTallerSerializer,
    ValoresEquipoAlquiladoTallerSerializer, CostoEquipoValoresTallerSerializer,
    LubricanteItemSerializer, ValoresByItemSerializer)
from api.filters import (
    PresupuestoFilter, CertificacionFilter, AvanceObraFilter,
    ProyeccionAvanceObraFilter, ProyeccionCertificacionFilter,
    ProyeccionCostoFilter, EquiposFilter, ParametrosGeneralesFilter,
    AsistenciaEquipoFilter, RegistroAsistenciaEquipoFilter,
    ValoresEquipoTallerFilter, TrenRodajeValoresTallerFilter,
    PosesionValoresTallerFilter, ReparacionesValoresTallerFilter,
    EquipoAlquiladoValoresTallerFilter, ManoObraValoresTallerFilter,
    CostoEquipoValoresTallerFilter)
from equipos.models import (
    ParametrosGenerales, AsistenciaEquipo, RegistroAsistenciaEquipo,
    CostoEquipoValores, TotalFlota, LubricantesValores, TrenRodajeValores,
    PosesionValores, ReparacionesValores, EquipoAlquiladoValores,
    ManoObraValores, LubricanteItem, LubricantesValoresItem)
from equipos.calculo_costos import get_stats_of_asistencia_by_cc
from equipos.excel import ExportReportTaller
from core.models import Obras, UserExtension, Equipos
from costos.models import CostoTipo, AvanceObra, Costo
from parametros.models import Periodo, FamiliaEquipo
from presupuestos.models import (
    Presupuesto, Revision, ItemPresupuesto)
from proyecciones.models import (
    ProyeccionAvanceObra, ProyeccionCertificacion, ProyeccionCosto)
from zweb_utils.views import generate_menu_user
from registro.models import Certificacion, TableroControlOS
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
        try:
            freeze = TableroControlOS.objects.get(periodo=periodo, obra=obra)
            data = json.loads(freeze.certificacion_data)
            return data
        except TableroControlOS.DoesNotExist:
            return get_certificacion_graph(obra, periodo)


class TCCostoGraphView(GraphDataMixin, AuthView):

    def get_data(self, obra, periodo):
        try:
            freeze = TableroControlOS.objects.get(periodo=periodo, obra=obra)
            data = json.loads(freeze.costos_data)
            return data
        except TableroControlOS.DoesNotExist:
            return get_costos_graph(obra, periodo)


class TCAvanceGraphView(GraphDataMixin, AuthView):
    def get_data(self, obra, periodo):
        try:
            freeze = TableroControlOS.objects.get(periodo=periodo, obra=obra)
            data = json.loads(freeze.avance_data)
            return data
        except TableroControlOS.DoesNotExist:
            return get_avances_graph(obra, periodo)


class TCConsolidadoGraphView(GraphDataMixin, AuthView):
    def get_data(self, obra, periodo):
        try:
            freeze = TableroControlOS.objects.get(periodo=periodo, obra=obra)
            data = json.loads(freeze.consolidado_data)
            return data
        except TableroControlOS.DoesNotExist:
            return get_consolidado_graph(obra, periodo)


class TableroControTablalView(GraphDataMixin, AuthView):
    def get_data(self, obra, periodo):
        try:
            freeze = TableroControlOS.objects.get(periodo=periodo, obra=obra)
            data = json.loads(freeze.tablero_data)
            data.update({
                'is_freeze': True,
                'pdf': freeze.pdf.url,
                'emitido': freeze.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                'info_obra': json.loads(freeze.info_obra),
                'revisiones_historico': json.loads(freeze.revisiones_historico)
                })
            return data
        except TableroControlOS.DoesNotExist:
            return generar_tabla_tablero(obra, periodo)


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

    @list_route(methods=['get'], url_path='activos')
    def activos(self, request):
        qs = self.get_queryset().exclude(fecha_fin__isnull=False)
        return Response({
            'count': qs.count(),
            'centros_costos': ObrasSerializer(qs, many=True).data
        })

    @list_route(methods=['get'], url_path='by-deposito')
    def by_deposito(self, request):
        qs = self.get_queryset().exclude(deposito__isnull=True)
        centro_costos = [{
            'id': cc.id,
            'obra': cc.obra,
            'codigo': cc.codigo,
            'deposito': cc.deposito
        } for cc in qs]
        return Response(centro_costos)


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


class ProyeccionCertificacionViewSet(ModelViewSet, AuthView):
    serializer_class = ProyeccionCertificacionSerializer
    filter_class = ProyeccionCertificacionFilter

    def get_queryset(self):
        obra_qs = self.get_centros_costos()
        return ProyeccionCertificacion.objects.filter(
            centro_costo__in=obra_qs).order_by('periodo__fecha_fin')


class ProyeccionCostoViewSet(ModelViewSet, AuthView):
    serializer_class = ProyeccionCostoSerializer
    filter_class = ProyeccionCostoFilter

    def get_queryset(self):
        obra_qs = self.get_centros_costos()
        return ProyeccionCosto.objects.filter(
            centro_costo__in=obra_qs).order_by('periodo__fecha_fin')


class TableroControlOSEmitidosView(ModelViewSet, AuthView):
    serializer_class = TableroControlOSSerializer

    def get_queryset(self):
        return TableroControlOS.objects.filter(obra__in=self.get_centros_costos())

    def get_serializer_context(self):
        return {'request': self.request}


class EquiposViewSet(ModelViewSet, AuthView):
    serializer_class = EquipoSerializer
    filter_class = EquiposFilter

    def get_queryset(self):
        return Equipos.objects.exclude(id=1).order_by('fecha_baja')

    @detail_route(methods=['post'], url_path='set-baja')
    def set_baja(self, request, pk):
        equipo = self.get_object()
        equipo.fecha_baja = timezone.now().date()
        equipo.save()
        return Response({'status': 'ok', 'equipo': EquipoSerializer(equipo).data})

    @list_route(methods=['get'], url_path='activos-taller')
    def activos(self, request):
        qs = Equipos.objects.exclude(
            (Q(fecha_baja__isnull=False) | Q(excluir_costos_taller=True)) | Q(pk=1)
        ).order_by('n_interno')
        return Response({
            'count': qs.count(),
            'equipos': EquipoSerializer(qs, many=True).data
        })

    @list_route(methods=['get'], url_path='alquilados-taller')
    def alquilados_en_taller(self, request):
        qs = Equipos.objects.exclude(
            (Q(fecha_baja__isnull=False) | Q(excluir_costos_taller=True)) | Q(pk=1)
        ).filter(es_alquilado=True).order_by('n_interno')
        return Response({
            'count': qs.count(),
            'equipos': EquipoSerializer(qs, many=True).data
        })

    @list_route(methods=['get'], url_path='propios-taller')
    def propios_en_taller(self, request):
        qs = Equipos.objects.exclude(
            (Q(fecha_baja__isnull=False) | Q(excluir_costos_taller=True)) | Q(pk=1)
        ).filter(es_alquilado=False).order_by('n_interno')
        return Response({
            'count': qs.count(),
            'equipos': EquipoSerializer(qs, many=True).data
        })

class FamiliaEquipoViewSet(ModelViewSet, AuthView):
    serializer_class = FamiliaEquipoSerializer

    def get_queryset(self):
        return FamiliaEquipo.objects.all()


class ParametrosGeneralesTallerViewSet(ModelViewSet, AuthView):
    serializer_class = ParametrosGeneralesTallerSerializer
    queryset = ParametrosGenerales.objects.all().order_by('-valido_desde__fecha_inicio')
    filter_class = ParametrosGeneralesFilter

    @list_route(methods=['get'], url_path='latest')
    def latest(self, request):
        return Response(ParametrosGeneralesTallerSerializer(
            self.queryset.latest('valido_desde__fecha_inicio')).data
        )


class AsistenciaEquipoViewSet(ModelViewSet, AuthView):
    serializer_class = AsistenciaEquipoSerializer
    filter_class = AsistenciaEquipoFilter

    def get_queryset(self):
        return AsistenciaEquipo.objects.all().order_by('-dia')


class RegistroAsistenciaEquipoViewSet(ModelViewSet, AuthView):
    serializer_class = RegistroAsistenciaEquipoSerializer
    filter_class = RegistroAsistenciaEquipoFilter

    def get_queryset(self):
        return RegistroAsistenciaEquipo.objects.all()


class ReportAsistenciaByEquipoView(AuthView):

    def get(self, request, *args, **kwargs):
        periodo = get_object_or_404(Periodo, pk=self.kwargs.get('pk'))
        data, raw = get_stats_of_asistencia_by_cc(periodo)
        serializer = ReportAsistenciaItemCCSerializer(data, many=True)
        return Response(serializer.data)


class ReportAsistenciaByCCDownloadView(AuthView):

    def get(self, request, *args, **kwargs):
        periodo = get_object_or_404(Periodo, pk=self.kwargs.get('pk'))
        centro_costo = get_object_or_404(Obras, pk=self.kwargs.get('cc_id'))
        xlsx_content = ExportReportTaller().report_asistencia_equipo_by_cc(periodo, centro_costo)
        response = HttpResponse(xlsx_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = u'attachment; filename="Informe de equipos (%s).xlsx"' % centro_costo
        return response


class ReportAsistenciaSummaryDownloadView(AuthView):

    def get(self, request, *args, **kwargs):
        periodo = get_object_or_404(Periodo, pk=self.kwargs.get('pk'))
        xlsx_content = ExportReportTaller().report_asistencia_equipo_summary(periodo)
        response = HttpResponse(xlsx_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = u'attachment; filename="Informe de equipos Resumen (%s).xlsx"' % periodo.descripcion
        return response


class CostoEquipoValoresTallerViewSet(ModelViewSet, AuthView):
    serializer_class = CostoEquipoValoresTallerSerializer
    queryset = CostoEquipoValores.objects.order_by('-valido_desde__fecha_inicio', 'equipo__n_interno')
    filter_class = CostoEquipoValoresTallerFilter

    @list_route(methods=['get'], url_path='latest')
    def latest(self, request):
        equipos = Equipos.objects.actives_in_cost().filter(es_alquilado=False).order_by("n_interno")
        valores = []
        for equipo in equipos:
            valor = CostoEquipoValores.objects.vigente_actual(equipo=equipo)
            if valor:
                valores.append(valor)
        if not valores:
            return Response({})
        parametros =  ParametrosGenerales.vigente(valores[0].valido_desde)
        param_serializer = ParametrosGeneralesTallerSerializer(parametros)
        serializer = CostoEquipoValoresTallerSerializer(valores, many=True)
        return Response({
            'latest': serializer.data,
            'parametros': param_serializer.data,
            'count': len(valores)
        })

    @atomic
    @list_route(methods=['post'], url_path='crear-nuevos')
    def crear_nuevos(self, request):
        periodo = get_object_or_404(Periodo, pk=request.GET.get('periodo_id'))
        serializer = CostoEquipoValoresTallerSerializer(data=request.data, many=True)
        serializer.is_valid()
        try:
            # uso el request porque no sé porque intenta serializer un equipo, y solo tengo el id
            for item in request.data:
                new_val = CostoEquipoValores()
                new_val.markup = D(item.get("markup"))
                new_val.equipo_id = item.get("equipo_id")
                new_val.valido_desde = periodo
                new_val.save()
            return Response({'status': 'ok', 'message': 'Valores creados correctamente.'})
        except Exception as ex:
            return Response({'status': 'error', 'message': str(ex)})


class TableroControlTallerView(ReadOnlyModelViewSet, AuthView):
    serializer_class = TableroControlTallerSerializer
    pagination_class = None

    def get_queryset(self):
        periodo = get_object_or_404(Periodo, pk=self.kwargs.get('periodo_pk'))
        equipos = Equipos.objects.actives_in_cost(periodo.fecha_inicio)
        valores = []
        for equipo in equipos:
            valores.append(CostoEquipoValores.objects.vigente(equipo=equipo, periodo=periodo))
        return valores

    def get_object(self):
        periodo = get_object_or_404(Periodo, pk=self.kwargs.get('periodo_pk'))
        equipo = get_object_or_404(Equipos, pk=self.kwargs.get('pk'))
        try:
            return CostoEquipoValores.objects.vigente(equipo=equipo, periodo=periodo)
        except CostoEquipoValores.DoesNotExist:
            raise Http404

    @list_route(methods=['get'], url_path='flota')
    def flota(self, request, periodo_pk):
        recalc = bool(request.GET.get('recalcular', False))
        periodo = get_object_or_404(Periodo, pk=periodo_pk)
        flota, _ = TotalFlota.objects.get_or_create(valido_desde=periodo)
        if recalc:
            flota.calcular_total_flota()
        return Response({
            'monto': "%.2f" % flota.monto,
            'cantidad': flota.cantidad
        })


class LubricantesValoresTallerViewSet(ModelViewSet, AuthView):
    serializer_class = ValoresLubricantesTallerSerializer
    queryset = LubricantesValores.objects.order_by('-valido_desde__fecha_inicio', 'equipo__n_interno')
    filter_class = ValoresEquipoTallerFilter

    @atomic
    @list_route(methods=['post'], url_path='crear-nuevos')
    def crear_nuevos(self, request):
        periodo = get_object_or_404(Periodo, pk=request.GET.get('periodo_id'))
        serializer = ValoresByItemSerializer(data=request.data, many=True)
        serializer.is_valid()
        equipos = Equipos.objects.actives_in_cost(periodo.fecha_inicio)
        try:
            for eq in equipos:
                # el agrupador de parametro de lubricantes vigentes
                lubri_param = eq.lubricantesparametros_set.order_by('-valido_desde__fecha_inicio').first()
                if lubri_param:
                    # tengo definicion de parametros. Busco todos los items asignados al equipo
                    item_parametros = lubri_param.items_lubricante.values_list('item', flat=True)
                    # creo el agrupador de valores para el equipo y periodo
                    lubri_valor = LubricantesValores.objects.create(equipo=eq, valido_desde=periodo)
                    # por cada item que tenga asignado este equipo, creo un LubricanteValoresItem asociado al Valor anterior
                    for item in serializer.data:
                        if item.get("item_id", 0) in item_parametros:
                            new_val = LubricantesValoresItem(
                                valor=lubri_valor,
                                item_id=item.get('item_id'),
                                valor_unitario=D(item.get('nuevo_valor', 0))
                            )
                            new_val.save()
            return Response({'status': 'ok', 'message': 'Valores creados correctamente.'})
        except Exception as ex:
            return Response({'status': 'error', 'message': str(ex)})


class LubricantesItemTallerViewSet(ModelViewSet, AuthView):
    serializer_class = LubricanteItemSerializer
    queryset = LubricanteItem.objects.all()

    @list_route(methods=['get'], url_path='latest')
    def latest(self, request):
        qs = self.get_queryset()
        last_periodo = 0
        valores = []
        for item in qs:
            valor = item.itemes.order_by('-valor__valido_desde__fecha_inicio').first()
            if valor:
                valores.append({'item_id': item.pk, 'valor': valor.valor_unitario})
                last_periodo = max(last_periodo, valor.valor.valido_desde.pk)
        return Response({
            'periodo_id': last_periodo,
            'valores': valores
        })


class TrenRodajeTallerViewSet(ModelViewSet, AuthView):
    serializer_class = ValoresTrenRodajeTallerSerializer
    queryset = TrenRodajeValores.objects.order_by('-valido_desde__fecha_inicio', 'equipo__n_interno')
    filter_class = TrenRodajeValoresTallerFilter

    @list_route(methods=['get'], url_path='latest')
    def latest(self, request):
        equipos = Equipos.objects.actives_in_cost().order_by("n_interno")
        valores = []
        for equipo in equipos:
            valor = TrenRodajeValores.objects.vigente_actual(equipo=equipo)
            if valor:
                valores.append(valor)
        if not valores:
            return Response([])
        parametros =  ParametrosGenerales.vigente(valores[0].valido_desde)
        param_serializer = ParametrosGeneralesTallerSerializer(parametros)
        serializer = ValoresTrenRodajeTallerSerializer(valores, many=True)
        return Response({
            'latest': serializer.data,
            'parametros': param_serializer.data,
            'count': len(valores)
        })

    @atomic
    @list_route(methods=['post'], url_path='crear-nuevos')
    def crear_nuevos(self, request):
        periodo = get_object_or_404(Periodo, pk=request.GET.get('periodo_id'))
        serializer = ValoresTrenRodajeTallerSerializer(data=request.data, many=True)
        serializer.is_valid()
        try:
            for item in serializer.data:
                new_val = TrenRodajeValores(
                    equipo_id=item.get("equipo_id"),
                    valido_desde=periodo,
                    precio_neumatico=item.get('precio_neumatico', None)
                    )
                new_val.save()
            return Response({'status': 'ok', 'message': 'Valores creados correctamente.'})
        except Exception as ex:
            return Response({'status': 'error', 'message': str(ex)})


class PosesionTallerViewSet(ModelViewSet, AuthView):
    serializer_class = ValoresPosesionTallerSerializer
    queryset = PosesionValores.objects.order_by('-valido_desde__fecha_inicio', 'equipo__n_interno')
    filter_class = PosesionValoresTallerFilter

    @list_route(methods=['get'], url_path='latest')
    def latest(self, request):
        equipos = Equipos.objects.actives_in_cost().order_by("n_interno")
        valores = []
        for equipo in equipos:
            valor = PosesionValores.objects.vigente_actual(equipo=equipo)
            if valor:
                valores.append(valor)
        if not valores:
            return Response({})
        parametros =  ParametrosGenerales.vigente(valores[0].valido_desde)
        param_serializer = ParametrosGeneralesTallerSerializer(parametros)
        serializer = ValoresPosesionTallerSerializer(valores, many=True)
        return Response({
            'latest': serializer.data,
            'parametros': param_serializer.data,
            'count': len(valores)
        })

    @atomic
    @list_route(methods=['post'], url_path='crear-nuevos')
    def crear_nuevos(self, request):
        periodo = get_object_or_404(Periodo, pk=request.GET.get('periodo_id'))
        serializer = ValoresPosesionTallerSerializer(data=request.data, many=True)
        serializer.is_valid()
        try:
            for item in serializer.data:
                val_dict = dict(item)
                val_dict.pop('pk')
                new_val = PosesionValores(**val_dict)
                new_val.equipo_id = item.get("equipo_id")
                new_val.valido_desde = periodo
                new_val.save()
            return Response({'status': 'ok', 'message': 'Valores creados correctamente.'})
        except Exception as ex:
            return Response({'status': 'error', 'message': str(ex)})


class ReparacionesTallerViewSet(ModelViewSet, AuthView):
    serializer_class = ValoresReparacionesTallerSerializer
    queryset = ReparacionesValores.objects.order_by('-valido_desde__fecha_inicio', 'equipo__n_interno')
    filter_class = ReparacionesValoresTallerFilter

    @list_route(methods=['get'], url_path='latest')
    def latest(self, request):
        equipos = Equipos.objects.actives_in_cost()
        valores = []
        for equipo in equipos:
            valores.append(ReparacionesValores.objects.vigente_actual(equipo=equipo))
        if not valores:
            return Response({})
        parametros =  ParametrosGenerales.vigente(valores[0].valido_desde)
        param_serializer = ParametrosGeneralesTallerSerializer(parametros)
        serializer = ValoresReparacionesTallerSerializer(valores, many=True)
        return Response({
            'latest': serializer.data,
            'parametros': param_serializer.data,
            'count': len(valores)
        })

    @list_route(methods=['post'], url_path='crear-nuevos')
    def crear_nuevos(self, request):
        periodo = get_object_or_404(Periodo, pk=request.data.get('periodo_pk'))
        equipos = Equipos.objects.actives_in_cost(periodo.fecha_inicio)
        try:
            valores = []
            for equipo in equipos:
                valores.append(ReparacionesValores(equipo=equipo, valido_desde=periodo))
            ReparacionesValores.objects.bulk_create(valores)
            return Response({'status': 'ok', 'message': '{} Valores creados'.format(len(valores))})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)})


class EquipoAlquiladoTallerViewSet(ModelViewSet, AuthView):
    serializer_class = ValoresEquipoAlquiladoTallerSerializer
    queryset = EquipoAlquiladoValores.objects.order_by('-valido_desde__fecha_inicio', 'equipo__n_interno')
    filter_class = EquipoAlquiladoValoresTallerFilter

    @list_route(methods=['get'], url_path='latest')
    def latest(self, request):
        equipos = Equipos.objects.actives_in_cost().filter(es_alquilado=True).order_by("n_interno")
        valores = []
        for equipo in equipos:
            valor = EquipoAlquiladoValores.objects.vigente_actual(equipo=equipo)
            if valor:
                valores.append(valor)
        if not valores:
            return Response({})
        parametros =  ParametrosGenerales.vigente(valores[0].valido_desde)
        param_serializer = ParametrosGeneralesTallerSerializer(parametros)
        serializer = ValoresEquipoAlquiladoTallerSerializer(valores, many=True)
        return Response({
            'latest': serializer.data,
            'parametros': param_serializer.data,
            'count': len(valores)
        })

    @atomic
    @list_route(methods=['post'], url_path='crear-nuevos')
    def crear_nuevos(self, request):
        periodo = get_object_or_404(Periodo, pk=request.GET.get('periodo_id'))
        serializer = ValoresEquipoAlquiladoTallerSerializer(data=request.data, many=True)
        serializer.is_valid()
        try:
            for item in serializer.data:
                val_dict = dict(item)
                val_dict.pop('pk', None)
                new_val = EquipoAlquiladoValores(**val_dict)
                new_val.equipo_id = item.get("equipo_id")
                new_val.valido_desde = periodo
                new_val.save()
            return Response({'status': 'ok', 'message': 'Valores creados correctamente.'})
        except Exception as ex:
            return Response({'status': 'error', 'message': str(ex)})



class ManoObraTallerViewSet(ModelViewSet, AuthView):
    serializer_class = ValoresManoObraTallerSerializer
    queryset = ManoObraValores.objects.order_by('-valido_desde__fecha_inicio')
    filter_class = ManoObraValoresTallerFilter
