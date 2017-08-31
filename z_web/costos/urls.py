from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.costos_list, name="costos_list"),
    url(r'^carga_cc/$', views.costos_alta_cc, name="costos_alta_cc"),
    url(r'^carga_eq/$', views.costos_alta_eq, name="costos_alta_eq"),
    url(r'^select_carga/$', views.costos_select, name="costos_select"),
    url(r'^copia_costos/$', views.copia_costos, name='copia_costos'),
    url(r'^editar/(?P<pk>\d+)/$', views.costos_edit, name="costos_edit"),
    url(r'^eliminar/(?P<pk>\d+)/$', views.costos_delete, name="costos_delete"),
    ]
