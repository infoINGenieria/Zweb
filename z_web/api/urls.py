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
    FamiliaEquipoViewSet
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

]
