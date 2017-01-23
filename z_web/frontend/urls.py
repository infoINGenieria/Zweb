from django.conf.urls import url

from frontend import views


urlpatterns = [
    url(r'^panel-control/$', views.ms_panel_control, name='ms_panel_control'),
    url(r'^panel-control/exportar_xls/$', views.ms_export_panel_control_excel, name='ms_export_panel_control_excel'),
]
