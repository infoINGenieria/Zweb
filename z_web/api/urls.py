# coding: utf-8

from django.conf.urls import url, include

from rest_framework import routers


from api.views import (
    PresupuestoViewSet, RevisionViewSet, TipoCostoViewSet,
    ItemPresupuestoViewSet, DynamicMenuView, CentroCostoViewSet,
    CertificacionRealViewSet,
    PeriodoViewSet, TableroControTablalView, TCCertficacionGraphView,
    TCCostoGraphView, TCAvanceGraphView, TCConsolidadoGraphView,
    AvanceObraViewSet, ProyeccionAvanceObraViewSet, ProyeccionCertificacionViewSet,
    ProyeccionCostoViewSet, TableroControlOSEmitidosView, EquiposViewSet,
    FamiliaEquipoViewSet, ParametrosGeneralesTallerViewSet, AsistenciaEquipoViewSet,
    RegistroAsistenciaEquipoViewSet, ReportAsistenciaByEquipoView,
    TableroControlTallerView, LubricantesValoresTallerViewSet, TrenRodajeTallerViewSet,
    PosesionTallerViewSet, ReparacionesTallerViewSet, EquipoAlquiladoTallerViewSet,
    ManoObraTallerViewSet, CostoEquipoValoresTallerViewSet, ReportAsistenciaByCCDownloadView,
    ReportAsistenciaSummaryDownloadView
)

router = routers.DefaultRouter()
router.register(
    r'presupuestos', PresupuestoViewSet, base_name='presupuesto')
router.register(
    r'presupuestos/(?P<presupuesto_pk>[^/.]+)/v',
    RevisionViewSet, base_name='revision')
# router.register(
#     r'presupuestos/(?P<presupuesto_pk>[^/.]+)/v/(?P<version>[^/.]+)/items',
#     ItemPresupuestoViewSet, base_name='revision')
router.register(
    r'tipo_costos', TipoCostoViewSet, base_name='tipo_costos')
router.register(
    r'centro_costos', CentroCostoViewSet, base_name='centro_costo'
)
router.register(
    r'centro_costos_emitidos', TableroControlOSEmitidosView, base_name='centro_costo_emitido'
)
router.register(
    r'certificaciones', CertificacionRealViewSet, base_name='certificacion'
)
router.register(
    r'periodos', PeriodoViewSet, base_name='periodo'
)
router.register(
    r'avanceobra', AvanceObraViewSet, base_name='avanceobra'
)
router.register(
    r'proyecciones/avance_obra', ProyeccionAvanceObraViewSet, base_name='proyeccion_avanceobra'
)
router.register(
    r'proyecciones/certificacion', ProyeccionCertificacionViewSet, base_name='proyeccion_certificacion'
)
router.register(
    r'proyecciones/costo', ProyeccionCostoViewSet, base_name='proyeccion_costo'
)
router.register(
    r'equipos', EquiposViewSet, base_name='equipos'
)
router.register(
    r'familia_equipos', FamiliaEquipoViewSet, base_name='familia_equipos'
)
router.register(
    r'taller/parametros_generales', ParametrosGeneralesTallerViewSet, base_name='parametros_generales'
)
router.register(
    r'taller/valores/lubricantes', LubricantesValoresTallerViewSet, base_name='valores_lubricantes'
)
router.register(
    r'taller/valores/tren_rodaje', TrenRodajeTallerViewSet, base_name='valores_tren_rodaje'
)
router.register(
    r'taller/valores/posesion', PosesionTallerViewSet, base_name='valores_posesion'
)
router.register(
    r'taller/valores/reparaciones', ReparacionesTallerViewSet, base_name='valores_reparaciones'
)
router.register(
    r'taller/valores/mano_obra', ManoObraTallerViewSet, base_name='valores_mano_obra'
)
router.register(
    r'taller/valores/alquilados', EquipoAlquiladoTallerViewSet, base_name='valores_alquilados'
)
router.register(
    r'taller/valores/markup', CostoEquipoValoresTallerViewSet, base_name='markup'
)
router.register(
    r'taller/asistencia', AsistenciaEquipoViewSet, base_name='asistencia_equipo'
)
router.register(
    r'taller/registros_asistencia', RegistroAsistenciaEquipoViewSet, base_name='registro_asistencia_equipo'
)
router.register(
    r'taller/tablero/(?P<periodo_pk>\d+)', TableroControlTallerView, base_name='taller_tablero_control'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^my_menu/', DynamicMenuView.as_view(), name="my_menu"),
    url(r'^tablero/(?P<un>[^/.]+)/(?P<obra_pk>\d+)/(?P<periodo_pk>\d+)/$',
        TableroControTablalView.as_view(), name="tablero_control_tabla"),
    url(r'^tablero/(?P<un>[^/.]+)/(?P<obra_pk>\d+)/(?P<periodo_pk>\d+)/graph_certificacion/$',
        TCCertficacionGraphView.as_view(), name="tablero_control_curva_cert"),
    url(r'^tablero/(?P<un>[^/.]+)/(?P<obra_pk>\d+)/(?P<periodo_pk>\d+)/graph_costo/$',
        TCCostoGraphView.as_view(), name="tablero_control_curva_costo"),
    url(r'^tablero/(?P<un>[^/.]+)/(?P<obra_pk>\d+)/(?P<periodo_pk>\d+)/graph_avance/$',
        TCAvanceGraphView.as_view(), name="tablero_control_curva_avance"),
    url(r'^tablero/(?P<un>[^/.]+)/(?P<obra_pk>\d+)/(?P<periodo_pk>\d+)/consolidado/$',
        TCConsolidadoGraphView.as_view(), name="tablero_control_consolidado"),
    url(r'^taller/asistencia/reportes/equipos/(?P<pk>[^/.]+)/',
        ReportAsistenciaByEquipoView.as_view(), name="taller_reporte_asistencia_equipo"),
    url(r'^taller/asistencia/reportes/cc/(?P<pk>[^/.]+)/(?P<cc_id>[^/.]+)/',
        ReportAsistenciaByCCDownloadView.as_view(), name="taller_reporte_asistencia_cc"),
    url(r'^taller/asistencia/reportes/summary/(?P<pk>[^/.]+)/',
        ReportAsistenciaSummaryDownloadView.as_view(), name="taller_reporte_asistencia_summary"),

]

