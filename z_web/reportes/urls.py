from django.conf.urls import url

from reportes import views


urlpatterns = [
    url(r'^$', views.reportes_index, name='index'),
    url(r'^operario-hora/$', views.operario_hora_reporte, name='operario_hora'),
]
