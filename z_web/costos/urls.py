from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.costos_list, name="costos_list"),
    url(r'^carga_cc/$', views.costos_alta_cc, name="costos_alta_cc"),
    url(r'^carga_eq/$', views.costos_alta_eq, name="costos_alta_eq"),
    url(r'^select_carga/$', views.costos_select, name="costos_select"),
    url(r'^select_carga/(?P<es_proyeccion>\w+)/$', views.costos_select, name="costos_select"),
    url(r'^copia_costos/$', views.copia_costos, name='copia_costos'),
    url(r'^editar/(?P<pk>\d+)/$', views.costos_edit, name="costos_edit"),
    url(r'^eliminar/(?P<pk>\d+)/$', views.costos_delete, name="costos_delete"),

    url(r'^avance-obra/$', views.avances_obra_list, name="avances_obra_list"),
    url(r'^avance-obra/cargar/$', views.avances_obra_create, name="avances_obra_create"),
    url(r'^avance-obra/editar/(?P<pk>\d+)/$', views.avances_obra_edit, name="avances_obra_edit"),
    url(r'^avance-obra/eliminar/(?P<pk>\d+)/$', views.avances_obra_delete, name="avances_obra_delete"),
    ]
