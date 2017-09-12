from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.costos_index, name="index"),
    url(r'^lista/$', views.costos_list, name="costos_list"),
    url(r'^carga_cc/$', views.costos_alta_cc, name="costos_alta_cc"),
    url(r'^carga_eq/$', views.costos_alta_eq, name="costos_alta_eq"),
    url(r'^select_carga/$', views.costos_select, name="costos_select"),
    url(r'^select_carga/(?P<es_proyeccion>\w+)/$', views.costos_select, name="costos_select"),
    url(r'^copia_costos/$', views.copia_costos, name='copia_costos'),
    url(r'^editar/(?P<pk>\d+)/$', views.costos_edit, name="costos_edit"),
    url(r'^eliminar/(?P<pk>\d+)/$', views.costos_delete, name="costos_delete"),
    url(r'^proyecciones/$', views.proyecciones_list, name="proyecciones_list"),
    url(r'^proyecciones/carga_cc/$', views.proyecciones_alta_cc, name="proyecciones_alta_cc"),
    url(r'^proyecciones/carga_eq/$', views.proyecciones_alta_eq, name="proyecciones_alta_eq"),
    url(r'^proyecciones/editar/(?P<pk>\d+)/$', views.proyecciones_edit, name="proyecciones_edit"),
    url(r'^proyecciones/eliminar/(?P<pk>\d+)/$', views.proyecciones_delete, name="proyecciones_delete"),
    url(r'^avance-obra/$', views.avances_obra_list, name="avances_obra_list"),
    url(r'^avance-obra/cargar/$', views.avances_obra_create, name="avances_obra_create"),
    url(r'^avance-obra/editar/(?P<pk>\d+)/$', views.avances_obra_edit, name="avances_obra_edit"),
    url(r'^avance-obra/eliminar/(?P<pk>\d+)/$', views.avances_obra_delete, name="avances_obra_delete"),
    url(r'^avance-obra/proyeccion/$', views.avances_obra_proyeccion_list, name="avances_obra_proyeccion_list"),
    url(r'^avance-obra/proyeccion/cargar/$', views.avances_obra_proyeccion_create, name="avances_obra_proyeccion_create"),
    url(r'^avance-obra/proyeccion/editar/(?P<pk>\d+)/$', views.avances_obra_proyeccion_edit, name="avances_obra_proyeccion_edit"),
    url(r'^avance-obra/proyeccion/eliminar/(?P<pk>\d+)/$', views.avances_obra_proyeccion_delete, name="avances_obra_proyeccion_delete"),
    ]
