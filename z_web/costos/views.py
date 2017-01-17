from functools import partial, wraps
from django.apps import apps
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.transaction import atomic
from django.views.generic import TemplateView, CreateView
from django.forms.utils import ErrorList
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from core.models import Obras
from parametros.models import Periodo, FamiliaEquipo
from zweb_utils.views import LoginAndPermissionRequiredMixin
from .models import (CostoSubContrato, CostoManoObra, CostoPosesion, ReserveReparaciones, TrenRodaje,
                     MaterialesTotal, LubricanteFluidosHidro, CostoParametro)
from .forms import PeriodoSelectForm, CostoItemForm, CostoItemFamiliaForm, CopiaCostoForm


class Index(LoginAndPermissionRequiredMixin, TemplateView):
    template_name = "costos/ingreso_masivo.html"
    permission_required = 'can_add_costos_masivo'
    permission_denied_message = "No posee los permisos suficientes para ingresar a esa sección"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        if 'copia_form' not in kwargs:
            context["copia_form"] = CopiaCostoForm()
        return context

    def post(self, request, *args, **kwargs):
        p_form = CopiaCostoForm(self.request.POST)

        if p_form.is_valid():
            return self.form_valid(p_form)
        else:
            return self.form_invalid(p_form)

    def form_invalid(self, p_form):
        return self.render_to_response(
            self.get_context_data(copia_form=p_form))

    def form_valid(self, form):
        tipos = form.cleaned_data["tipo_costos"]
        de_periodo= form.cleaned_data["de_periodo"]
        a_periodo = form.cleaned_data["a_periodo"]
        recalcular = form.cleaned_data["recalcular"]
        if recalcular:
            try:
                des_param = CostoParametro.objects.get(periodo=a_periodo)
                # ori_param = CostoParametro.objects.get(periodo=de_periodo)
            except CostoParametro.DoesNotExist:
                messages.add_message(self.request, messages.ERROR,
                                     mark_safe("Asegúrese de definir los <a href='/costos/costoparametro'>parámetros "
                                               "de costos</a> para ambos periodos seleccionados."))
                return self.form_invalid(form)
        copia_dict = dict()
        for costo in tipos:
            model = apps.get_model(app_label='costos', model_name=costo)
            try:
                with atomic():
                    for obj in model.objects.filter(periodo=de_periodo):
                        copia_dict[costo] = True
                        obj.pk = None
                        if recalcular:
                            obj.recalcular_valor(des_param)
                        obj.periodo = a_periodo
                        obj.save()
            except IntegrityError:
                copia_dict[costo] = False
        for costo in tipos:
            if costo in copia_dict:
                if copia_dict[costo]:
                    messages.add_message(self.request, messages.SUCCESS,
                                         "Se crearon ítems de {} para el periodo {}".format(
                                                 dict(form.TIPO_COSTO)[costo], a_periodo))
                else:
                    messages.add_message(self.request, messages.WARNING,
                                         "Ya existen ítems de {} para el periodo {}. Debe utilizar "
                                         "la herramienta Ingreso Masivo Manual.".format(
                                                 dict(form.TIPO_COSTO)[costo], a_periodo))
            else:
                messages.add_message(self.request, messages.WARNING,
                                     "No existen ítems de {} para el periodo {}".format(dict(form.TIPO_COSTO)[costo], de_periodo))
        return HttpResponseRedirect(reverse('costos:index'))


class IngresoMasivoMixin(LoginAndPermissionRequiredMixin):
    """
    Se debe definir en la subclase de TemplateView:
    TITLE_TIPO_COSTO: con el titulo para el formulario
    template_name: esto lo necesita TemplateView
    form_class: clase de form utilizada en el formset
    specified_field: nombre del campo particular de la subclase
    """
    permission_required = 'can_add_costos_masivo'
    permission_denied_message = "No posee los permisos suficientes para ingresar a esa sección"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(IngresoMasivoMixin, self).get_context_data(**kwargs)
        context["periodo"] = Periodo.objects.order_by('-fecha_inicio')
        context["title_tipo_costo"] = self.TITLE_TIPO_COSTO
        context["{}s".format(self.specified_field)] = self.get_queryset()
        if "p_form" not in kwargs:
            context["p_form"] = PeriodoSelectForm()
        if "formsets" not in kwargs:
            CustomFormset = formset_factory(self.form_class, extra=0)
            initial = [{self.specified_field: x.pk} for x in self.get_queryset()]
            context["formsets"] = CustomFormset(initial=initial)
        return context

    def get_queryset(self):
        raise ImproperlyConfigured

    def post(self, request, *args, **kwargs):
        p_form = PeriodoSelectForm(self.request.POST)
        formsets = formset_factory(self.form_class, extra=0)(self.request.POST)

        if p_form.is_valid() and formsets.is_valid():
            return self.form_valid(p_form, formsets)
        else:
            return self.form_invalid(p_form, formsets)

    def form_invalid(self, p_form, formsets):
        return self.render_to_response(
            self.get_context_data(p_form=p_form, formsets=formsets))

    def response_result(self, p_form, formsets, periodo):
        if periodo:
            messages.add_message(self.request, messages.SUCCESS,
                                 "Se añadieron correctamente todos los valores de {} para el periodo {}".format(
                                         self.model._meta.verbose_name_plural, periodo))
            return HttpResponseRedirect(reverse('costos:index'))
        else:
            messages.add_message(self.request, messages.WARNING,
                                 "No íngresó valores de {}".format(
                                         self.model._meta.verbose_name_plural))
            return self.form_invalid(p_form, formsets)


class IngresoMasivoConObraMixin(IngresoMasivoMixin):
    TITLE_TIPO_COSTO = ''
    template_name = "costos/masivo_obra_form.html"
    form_class = CostoItemForm
    specified_field = 'obra'

    def get_queryset(self):
        return Obras.objects.filter(es_cc=True)


    def form_valid(self, p_form, formsets):
        has_error = False
        periodo = None
        try:
            with atomic():

                for f in formsets:
                    if f.cleaned_data["monto"]:
                        if not periodo:
                            periodo = p_form.cleaned_data["periodo"]
                        obra = f.cleaned_data["obra"]
                        if self.model.objects.filter(periodo=periodo, obra=obra).exists():
                            errors = f._errors.setdefault("monto", ErrorList())
                            errors.append(u"Ya existe un valor para el periodo seleccionado.")
                            has_error = True
                        else:
                            sub_contr = self.model()
                            sub_contr.obra = obra
                            sub_contr.monto = f.cleaned_data["monto"]
                            sub_contr.periodo = periodo
                            sub_contr.save()
                if has_error:
                    raise IntegrityError
        except IntegrityError:
            return self.form_invalid(p_form, formsets)
        return self.response_result(p_form, formsets, periodo)


class IngresoMasivoConFamiliaEquipoMixin(IngresoMasivoMixin):
    TITLE_TIPO_COSTO = ''
    template_name = "costos/masivo_familia_form.html"
    form_class = CostoItemFamiliaForm
    specified_field = 'familia'

    def get_queryset(self):
        return FamiliaEquipo.objects.all()

    def form_valid(self, p_form, formsets):
        has_error = False
        periodo = None
        try:
            with atomic():

                for f in formsets:
                    if f.cleaned_data["monto_hora"] or f.cleaned_data["monto_mes"]:
                        if not periodo:
                            periodo = p_form.cleaned_data["periodo"]
                            parametros = CostoParametro.objects.get(periodo=periodo)
                        familia = f.cleaned_data["familia"]
                        if self.model.objects.filter(periodo=periodo, familia_equipo=familia).exists():
                            errors = f._errors.setdefault("monto_mes", ErrorList())
                            errors.append(u"Ya existe un valor para el periodo seleccionado.")
                            has_error = True
                        else:
                            sub_contr = self.model()
                            sub_contr.familia_equipo = familia
                            if f.cleaned_data["monto_hora"] and not f.cleaned_data["monto_mes"]:
                                sub_contr.monto_hora = f.cleaned_data["monto_hora"]
                                sub_contr.set_monto_mes(parametros)
                            elif f.cleaned_data["monto_mes"] and not f.cleaned_data["monto_hora"]:
                                sub_contr.monto_mes = f.cleaned_data["monto_mes"]
                                sub_contr.set_monto_hora(parametros)
                            else:
                                sub_contr.monto_hora = f.cleaned_data["monto_hora"]
                                sub_contr.monto_mes = f.cleaned_data["monto_mes"]
                            sub_contr.periodo = periodo
                            sub_contr.save()
                if has_error:
                    raise IntegrityError
        except CostoParametro.DoesNotExist:
            messages.add_message(self.request, messages.ERROR,
                                 mark_safe("No están definidos los <a href='/costos/costoparametro'>parámetros de costos</a> para el "
                                       "periodo {}".format(periodo)))
            return self.form_invalid(p_form, formsets)
        except IntegrityError as e:
            return self.form_invalid(p_form, formsets)
        return self.response_result(p_form, formsets, periodo)


class SubcontratoMasivoView(IngresoMasivoConObraMixin, TemplateView):
    model = CostoSubContrato
    TITLE_TIPO_COSTO = "Costos de subcontratos"


class ManoObraMasivoView(IngresoMasivoConObraMixin, TemplateView):
    model = CostoManoObra
    TITLE_TIPO_COSTO = "Costos de mano de obra"


class TotalMaterialesView(IngresoMasivoConObraMixin, TemplateView):
    model = MaterialesTotal
    TITLE_TIPO_COSTO = "Costos totales de materiales"


class LubricanteFluidosHidroView(IngresoMasivoConFamiliaEquipoMixin, TemplateView):
    model = LubricanteFluidosHidro
    TITLE_TIPO_COSTO = "Costos de Lubricantes y Fluídos Hidráulicos"


class TrenRodajeView(IngresoMasivoConFamiliaEquipoMixin, TemplateView):
    model = TrenRodaje
    TITLE_TIPO_COSTO = "Costos de tren de rodaje"


class ReservaReparacionesView(IngresoMasivoConFamiliaEquipoMixin, TemplateView):
    model = ReserveReparaciones
    TITLE_TIPO_COSTO = "Reserva para reparaciones"


class CostosPosesionView(IngresoMasivoConFamiliaEquipoMixin, TemplateView):
    model = CostoPosesion
    TITLE_TIPO_COSTO = "Costos de posesión de equipo"


index = Index.as_view()
masivo_subcontrato = SubcontratoMasivoView.as_view()
masivo_manoobra = ManoObraMasivoView.as_view()
masivo_total_materiales = TotalMaterialesView.as_view()
masivo_lubricantes = LubricanteFluidosHidroView.as_view()

masivo_tren_rodaje = TrenRodajeView.as_view()
masivo_reserva_reparaciones = ReservaReparacionesView.as_view()
masivo_posesion = CostosPosesionView.as_view()