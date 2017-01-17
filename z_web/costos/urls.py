from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^subcontrato/$', views.masivo_subcontrato, name='masivo_subcontrato'),
    url(r'^manoobra/$', views.masivo_manoobra, name='masivo_manoobra'),
    url(r'^materiales/$', views.masivo_total_materiales, name='masivo_total_materiales'),
    url(r'^lubricantes/$', views.masivo_lubricantes, name='masivo_lubricantes'),

    url(r'^trenrodaje/$', views.masivo_tren_rodaje, name='masivo_tren_rodaje'),
    url(r'^reservareparacion/$', views.masivo_reserva_reparaciones, name='masivo_reserva_reparaciones'),
    url(r'^posesion/$', views.masivo_posesion, name='masivo_posesion'),
    ]
