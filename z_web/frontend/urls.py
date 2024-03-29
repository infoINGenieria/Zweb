from django.conf.urls import url

from frontend import views


urlpatterns = [
    url(r'^~/', views.ng_index, name='ng_index'),
    url(r'^panel-control/$', views.ms_panel_control, name='ms_panel_control'),
    url(r'^panel-control-rango/$', views.ms_custom_panel_control, name='ms_custom_panel_control'),
    url(r'^panel-control/exportar_xls/$', views.ms_export_panel_control_excel,
        name='ms_export_panel_control_excel'),
    url(r'^panel-control-rango/exportar_xls/$', views.ms_export_custom_panel_control_excel,
        name='ms_export_custom_panel_control_excel'),
]
