# coding: utf-8

from django.conf.urls import url, include

from rest_framework import routers


from api.views import (
    PresupuestoViewSet, RevisionViewSet, TipoItemPresupuestoViewSet,
    ItemPresupuestoViewSet
)

router = routers.DefaultRouter()
router.register(
    r'presupuestos', PresupuestoViewSet, base_name='presupuesto')
router.register(
    r'presupuestos/(?P<presupuesto_pk>[^/.]+)/v',
    RevisionViewSet, base_name='revision')
router.register(
    r'presupuestos/(?P<presupuesto_pk>[^/.]+)/v/(?P<version>[^/.]+)/items',
    ItemPresupuestoViewSet, base_name='revision')
router.register(
    r'tipo_items', TipoItemPresupuestoViewSet, base_name='tipo_item')


urlpatterns = [
    url(r'^', include(router.urls))
]
