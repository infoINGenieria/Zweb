# coding: utf-8

from django.conf.urls import url, include

from rest_framework import routers


from api.views import (
    PresupuestoViewSet, RevisionViewSet, TipoItemPresupuestoViewSet,
    ItemPresupuestoViewSet, DynamicMenuView, CentroCostoViewSet
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
    r'tipo_items', TipoItemPresupuestoViewSet, base_name='tipo_item')
router.register(
    r'centro_costos', CentroCostoViewSet, base_name='centro_costo'
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^my_menu/', DynamicMenuView.as_view(), name="my_menu"),

]
