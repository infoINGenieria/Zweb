# coding: utf-8

from django.conf.urls import url, include

from rest_framework import routers


from api.views import (
    PresupuestoViewSet, RevisionViewSet, TipoCostoViewSet,
    ItemPresupuestoViewSet, DynamicMenuView, CentroCostoViewSet,
    CertificacionRealViewSet, CertificacionProyeccionViewSet,
    PeriodoViewSet, TableroControlView
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
    r'certificaciones_real', CertificacionRealViewSet, base_name='certificacion_real'
)
router.register(
    r'certificaciones_proyeccion', CertificacionProyeccionViewSet, base_name='certificacion_proyeccion'
)
router.register(
    r'periodos', PeriodoViewSet, base_name='periodo'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^my_menu/', DynamicMenuView.as_view(), name="my_menu"),
    url(r'^tablero/(?P<un>[^/.]+)/(?P<obra_pk>\d+)/(?P<periodo_pk>\d+)/',
        TableroControlView.as_view(), name="tablero_control")

]
