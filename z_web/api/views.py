# coding: utf-8
from django.http import Http404, HttpResponse

from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed, ValidationError, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet, ModelViewSet

from api.serializers import (
    PresupuestoSerializer, RevisionSerializer, TipoItemPresupuestoSerializer,
    ItemPresupuestoSerializer, ObrasSerializer, CertificacionProyeccionSerializer,
    CertificacionRealSerializer, CertificacionItemSerializer, PeriodoSerializer)
from api.filters import PresupuestoFilter, CertificacionFilter
from core.models import Obras, UserExtension
from parametros.models import Periodo
from presupuestos.models import (
    Presupuesto, Revision, ItemPresupuesto, TipoItemPresupuesto)
from zweb_utils.views import generate_menu_user
from registro.models import CertificacionProyeccion, CertificacionReal, Certificacion


class AuthView(APIView):
    """
    Base class to endpoint views.
    """
    permission_classes = (IsAuthenticated, )


class DynamicMenuView(APIView):
    def get(self, request, *args, **kwargs):
        menu = generate_menu_user(request.user)
        return Response(menu)


class PresupuestoRelatedMixin(object):
    """
    Este mixin obtiene el id de presupuesto de la url.
    Usar en endpoint anidados a presupuesto
    """

    def initial(self, request, *args, **kwargs):
        presupuesto_pk = self.kwargs.get('presupuesto_pk')
        try:
            self.presupuesto = Presupuesto.objects.get(pk=presupuesto_pk)
        except Presupuesto.DoesNotExist:
            raise Http404
        return super(PresupuestoRelatedMixin, self).initial(request, *args, **kwargs)

    def get_serializer_context(self):
        """
        Poner el presupuestoen el contexto del serializer
        """
        return {'presupuesto_pk': self.kwargs["presupuesto_pk"]}


class PresupuestoViewSet(ModelViewSet, AuthView):
    serializer_class = PresupuestoSerializer
    filter_class = PresupuestoFilter

    def get_queryset(self):
        qs = Presupuesto.objects.all()
        return qs


class RevisionViewSet(PresupuestoRelatedMixin, ModelViewSet, AuthView):
    serializer_class = RevisionSerializer

    def get_queryset(self):
        qs = Revision.objects.filter(presupuesto=self.presupuesto)
        return qs.order_by('-version')

    def perform_create(self, serializer):
        serializer.save(presupuesto=self.presupuesto)

    def get_object(self):
        try:
            return Revision.objects.get(
                presupuesto=self.presupuesto,
                version=self.kwargs.get('pk'))
        except Revision.DoesNotExist:
            raise Http404


class ItemPresupuestoViewSet(PresupuestoRelatedMixin, ModelViewSet, AuthView):
    serializer_class = ItemPresupuestoSerializer

    def initial(self, request, *args, **kwargs):
        _super = super(ItemPresupuestoViewSet, self).initial(request, *args, **kwargs)
        version = self.kwargs.get('version')
        try:
            self.revision = Revision.objects.get(presupuesto=self.presupuesto, version=version)
        except Revision.DoesNotExist:
            raise Http404
        return _super

    def get_queryset(self):
        return ItemPresupuesto.objects.filter(revision=self.revision)

    def perform_create(self, serializer):
        serializer.save(revision=self.revision)


class TipoItemPresupuestoViewSet(ModelViewSet, AuthView):
    serializer_class = TipoItemPresupuestoSerializer
    queryset = TipoItemPresupuesto.objects.all()

    def destroy(self, *args, **kwargs):
        obj = self.get_object()
        if ItemPresupuesto.objects.filter(tipo=obj).exists():
            raise ParseError("Hay presupuestos utilizando este Tipo de "
                             "ítem de presupuesto. No se puede eliminar.")
            # return Response(data={'message': "Too late to delete"},
                            # status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CentroCostoViewSet(ModelViewSet, AuthView):
    serializer_class = ObrasSerializer

    def get_queryset(self):
        qs = Obras.objects.filter(es_cc=True)
        user = self.request.user
        try:
            if user.extension.unidad_negocio:
                qs = qs.filter(unidad_negocio=user.extension.unidad_negocio)
        except UserExtension.DoesNotExist:
            pass
        return qs


class CertificacionRealViewSet(ModelViewSet, AuthView):
    serializer_class = CertificacionRealSerializer
    filter_class = CertificacionFilter

    def get_centros_costos(self):
        obra_qs = Obras.objects.filter(es_cc=True)
        user = self.request.user
        try:
            if user.extension.unidad_negocio:
                obra_qs = obra_qs.filter(unidad_negocio=user.extension.unidad_negocio)
        except UserExtension.DoesNotExist:
            pass
        return obra_qs

    def get_queryset(self):
        obra_qs = self.get_centros_costos()
        return CertificacionReal.objects.filter(obra__in=obra_qs).order_by('-periodo__fecha_fin')


class CertificacionProyeccionViewSet(ModelViewSet, AuthView):
    serializer_class = CertificacionProyeccionSerializer
    filter_class = CertificacionFilter

    def get_centros_costos(self):
        obra_qs = Obras.objects.filter(es_cc=True)
        user = self.request.user
        try:
            if user.extension.unidad_negocio:
                obra_qs = obra_qs.filter(unidad_negocio=user.extension.unidad_negocio)
        except UserExtension.DoesNotExist:
            pass
        return obra_qs

    def get_queryset(self):
        obra_qs = self.get_centros_costos()
        return CertificacionProyeccion.objects.filter(obra__in=obra_qs).order_by('-periodo__fecha_fin')


class PeriodoViewSet(ModelViewSet, AuthView):
    serializer_class = PeriodoSerializer
    queryset = Periodo.objects.all().order_by('-fecha_fin')
