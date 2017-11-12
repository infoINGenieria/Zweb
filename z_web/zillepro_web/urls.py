"""zillepro_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views

from frontend.views import index
from zweb_utils.views import logout

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^', include('frontend.urls', namespace='frontend', app_name='frontend')),
    url(r'^reportes/', include('reportes.urls', namespace='reportes')),
    url(r'^costos/', include('costos.urls', namespace='costos', app_name='costos')),
    url(r'^presupuestos/', include('presupuestos.urls', namespace='presupuestos')),
    url(r'^api/', include('api.urls')),
    # admin
    url(r'^admin/', include(admin.site.urls)),
]

urlpatterns += [
    url(r'^logout/', logout, name='logout'),
    url(r'^login/$', views.login, {'template_name': 'auth/login.html'}, name='login'),
    url(r'^password_change/$', views.password_change, {'template_name': 'auth/password_change_form.html'},
        name='password_change'),
    url(r'^password_change/done/$', views.password_change_done, {'template_name': 'auth/password_change_done.html'},
        name='password_change_done'),
    url(r'^password_reset/$', views.password_reset, {
            'html_email_template_name': 'auth/password_reset_email.html',
            'template_name': 'auth/password_reset_form.html'
        }, name='password_reset'),
    url(r'^password_reset/done/$', views.password_reset_done, {'template_name': 'auth/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm, {'template_name': 'auth/password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^reset/done/$', views.password_reset_complete, {'template_name': 'auth/password_reset_complete.html'},
        name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
