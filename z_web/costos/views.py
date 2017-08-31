# coding: utf-8
from functools import partial, wraps
from django.apps import apps
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import IntegrityError
from django.db.transaction import atomic
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from django.forms.utils import ErrorList
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.shortcuts import render

from core.models import Obras
from parametros.models import Periodo, FamiliaEquipo
from zweb_utils.mixins import TableFilterListView, ModalViewMixin
from zweb_utils.views import LoginAndPermissionRequiredMixin
from .models import CostoParametro, Costo, CostoTipo
from .forms import (PeriodoSelectForm, CostoItemForm, CostoItemFamiliaForm,
                    CopiaCostoForm, CostoCCForm, PeriodoCCForm, PeriodoCostoTipoForm,
                    CostoEquipoForm, CostoEditPorCCForm, CostoEditPorEquipoForm)
from .tables import (CostosByCCMontoHSTable, CostosByCCTotalTable,
                     CostosByEquipoMontoHSTable, CostosByEquipoTotalTable)
from .filters import CostosFilter


class CopiaCostosView(LoginAndPermissionRequiredMixin, TemplateView):
    """
    Vista para copiar costos de un periodo a otro.
    """
    template_name = "frontend/costos/copiar_costos.html"
    permission_required = 'costos.can_manage_costos'
    permission_denied_message = "No posee los permisos suficientes para ingresar a esa sección"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(CopiaCostosView, self).get_context_data(**kwargs)
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
                                     mark_safe("Asegúrese de definir los <b><a href='{}'>parámetros "
                                               "de costos</a></b> para ambos periodos seleccionados.".format(
                                         reverse('admin:costos_costoparametro_changelist'))))
                return self.form_invalid(form)
        copia_dict = dict()
        for tipo_costo in tipos:
            with atomic():
                for obj in Costo.objects.filter(tipo_costo=tipo_costo, periodo=de_periodo):
                    try:
                        if tipo_costo not in copia_dict:
                            copia_dict[tipo_costo] = True
                        obj.pk = None
                        if recalcular:
                            obj.recalcular_valor(des_param)
                        obj.periodo = a_periodo
                        obj.clean()
                        obj.save()
                    except (IntegrityError, ValidationError):
                        copia_dict[tipo_costo] = False
        for tipo_costo in tipos:
            if tipo_costo in copia_dict:
                if copia_dict[tipo_costo]:
                    messages.add_message(
                        self.request, messages.SUCCESS,
                        mark_safe("Se crearon ítems de <b>{}</b> para el periodo {}".format(tipo_costo.nombre, a_periodo)))
                else:
                    messages.add_message(
                        self.request, messages.WARNING,
                        mark_safe("Hecho! Existían previamente ítems de <b>{}</b> para el periodo {}. Puede editarlos haciendo clic <a href='{}?tipo_costo={}&periodo={}'><b>acá</b></a>.".format(
                            tipo_costo, a_periodo, reverse('costos:costos_list'), tipo_costo.pk, a_periodo.pk)))
            else:
                messages.add_message(
                    self.request, messages.WARNING,
                    mark_safe("No existen ítems de <b>{}</b> para el periodo {}".format(tipo_costo, de_periodo)))
        return HttpResponseRedirect(reverse('costos:copia_costos'))


class CostosList(LoginAndPermissionRequiredMixin, TableFilterListView):
    permission_required = 'costos.can_manage_costos'
    permission_denied_message = "No posee los permisos suficientes para ingresar a esa sección"
    raise_exception = True
    model = Costo
    context_object_name = 'costos'
    template_name = 'frontend/costos/costo_list.html'
    # table_class = TurnosReporteTable
    filterset_class = CostosFilter

    def get_table_class(self, **kwargs):
        if self.filterset.form.is_valid():
            tipo_costo = self.filterset.form.cleaned_data["tipo_costo"]
            if tipo_costo.es_monto_segmentado:
                if tipo_costo.es_por_cc:
                    return CostosByCCMontoHSTable
                else:
                    return CostosByEquipoMontoHSTable
            else:
                if tipo_costo.es_por_cc:
                    return CostosByCCTotalTable
                else:
                    return CostosByEquipoTotalTable

        return CostosByCCMontoHSTable

    def get_context_data(self, **kwargs):
        ctx = super(CostosList, self).get_context_data(**kwargs)
        ctx["is_filtered"] = self.filterset.form.is_valid()
        return ctx


class CostosAltaCC(LoginAndPermissionRequiredMixin, TemplateView):
    permission_required = 'costos.can_manage_costos'
    permission_denied_message = "No posee los permisos suficientes para ingresar a esa sección"
    raise_exception = True

    template_name = "frontend/costos/costos_cc_form.html"

    def get_context_data(self, **kwargs):
        context = super(CostosAltaCC, self).get_context_data(**kwargs)
        # context["periodo"] = Periodo.objects.order_by('-fecha_inicio')
        # context["title_tipo_costo"] = "Carga de costos"
        context["tipos_costos"] = self.get_queryset()
        # context["{}s".format(self.specified_field)] = self.get_queryset()
        if "p_form" not in kwargs:
            context["p_form"] = PeriodoCCForm()
        if "formsets" not in kwargs:
            Formset = formset_factory(CostoCCForm, extra=0)
            initial = [{'tipo_costo': x.pk} for x in context["tipos_costos"]]
            context["formsets"] = Formset(initial=initial)
        return context

    def get_queryset(self, **kwargs):
        return CostoTipo.objects.filter(relacionado_con='cc')

    def post(self, request, *args, **kwargs):
        p_form = PeriodoCCForm(self.request.POST)
        formsets = formset_factory(CostoCCForm, extra=0)(self.request.POST)

        if p_form.is_valid() and formsets.is_valid():
            return self.form_valid(p_form, formsets)
        else:
            return self.form_invalid(p_form, formsets)

    def form_invalid(self, p_form, formsets):
        return self.render_to_response(self.get_context_data(p_form=p_form, formsets=formsets))

    def form_valid(self, p_form, formsets):
        has_error = False
        periodo = p_form.cleaned_data["periodo"]
        centro_costo = p_form.cleaned_data["centro_costo"]
        saved_count = 0
        try:
            with atomic():
                for f in formsets:
                    if f.cleaned_data["monto_total"]:
                        tipo_costo = f.cleaned_data["tipo_costo"]
                        if Costo.objects.filter(
                            periodo=periodo, centro_costo=centro_costo, tipo_costo=tipo_costo).exists():
                            errors = f._errors.setdefault("monto_total", ErrorList())
                            errors.append(u"Ya existe un valor para el periodo y centro de costo seleccionado.")
                            has_error = True
                        else:
                            costo = Costo(**f.cleaned_data)
                            costo.centro_costo = centro_costo
                            costo.periodo = periodo
                            costo.save()
                            saved_count += 1
                if has_error:
                    raise IntegrityError
        except IntegrityError:
            return self.form_invalid(p_form, formsets)
        return self.response_result(p_form, formsets, saved_count)

    def response_result(self, p_form, formsets, saved_count):
        if saved_count:
            messages.add_message(
                self.request, messages.SUCCESS,
                "Se añadieron correctamente {} costos al centro de costos '{}' para el periodo '{}'".format(
                    saved_count, p_form.cleaned_data["centro_costo"], p_form.cleaned_data["periodo"]))
            return HttpResponseRedirect(reverse('costos:costos_alta_cc'))
        else:
            messages.add_message(self.request, messages.WARNING, "No íngresó valores de costos")
            return self.form_invalid(p_form, formsets)


class CostosAltaEquipos(LoginAndPermissionRequiredMixin, TemplateView):
    permission_required = 'costos.can_manage_costos'
    permission_denied_message = "No posee los permisos suficientes para ingresar a esa sección"
    raise_exception = True
    template_name = "frontend/costos/costos_eq_form.html"
    form_class = CostoItemForm

    def get_context_data(self, **kwargs):
        context = super(CostosAltaEquipos, self).get_context_data(**kwargs)
        context["familias"] = self.get_queryset()
        # context["{}s".format(self.specified_field)] = self.get_queryset()
        if "p_form" not in kwargs:
            context["p_form"] = PeriodoCostoTipoForm()
        if "formsets" not in kwargs:
            Formset = formset_factory(CostoEquipoForm, extra=0)
            initial = [{'familia_equipo': x.pk} for x in context["familias"]]
            context["formsets"] = Formset(initial=initial)
        return context

    def get_queryset(self, **kwargs):
        return FamiliaEquipo.objects.all()

    def post(self, request, *args, **kwargs):
        p_form = PeriodoCostoTipoForm(self.request.POST)
        formsets = formset_factory(CostoEquipoForm, extra=0)(self.request.POST)

        if p_form.is_valid() and formsets.is_valid():
            return self.form_valid(p_form, formsets)
        else:
            return self.form_invalid(p_form, formsets)

    def form_invalid(self, p_form, formsets):
        return self.render_to_response(self.get_context_data(p_form=p_form, formsets=formsets))

    def form_valid(self, p_form, formsets):
        has_error = False
        periodo = p_form.cleaned_data["periodo"]
        tipo_costo = p_form.cleaned_data["tipo_costo"]
        saved_count = 0
        try:
            with atomic():
                for f in formsets:
                    if f.cleaned_data["monto_hora"] or f.cleaned_data["monto_mes"] or f.cleaned_data["monto_anio"]:
                        familia = f.cleaned_data["familia_equipo"]
                        if Costo.objects.filter(
                            periodo=periodo, familia_equipo=familia, tipo_costo=tipo_costo).exists():
                            errors = f._errors.setdefault("monto_hora", ErrorList())
                            errors.append(u"Ya existe un valor para el periodo y familia de equipos seleccionado.")
                            has_error = True
                        else:
                            costo = Costo(**f.cleaned_data)
                            costo.tipo_costo = tipo_costo
                            costo.periodo = periodo
                            costo.save()
                            saved_count += 1
                if has_error:
                    raise IntegrityError
        except CostoParametro.DoesNotExist:
            messages.add_message(
                self.request, messages.ERROR,
                mark_safe("No están definidos los <a href='{}'>parámetros de costos</a> para el "
                          "periodo {}".format(reverse('admin:costos_costoparametro_changelist'), periodo)))
            return self.form_invalid(p_form, formsets)
        except IntegrityError:
            return self.form_invalid(p_form, formsets)
        return self.response_result(p_form, formsets, saved_count)

    def response_result(self, p_form, formsets, saved_count):
        if saved_count:
            messages.add_message(
                self.request, messages.SUCCESS,
                "Se añadieron correctamente {} costos del tipo '{}' para el periodo '{}'".format(
                    saved_count, p_form.cleaned_data["tipo_costo"], p_form.cleaned_data["periodo"]))
            return HttpResponseRedirect(reverse('costos:costos_alta_eq'))
        else:
            messages.add_message(self.request, messages.WARNING, "No íngresó valores de costos")
            return self.form_invalid(p_form, formsets)


class CargarCostosSelectView(LoginAndPermissionRequiredMixin, TemplateView):
    template_name = 'frontend/costos/modal/cargar_costos_select.html'
    permission_required = 'costos.can_manage_costos'
    permission_denied_message = "No posee los permisos suficientes para ingresar a esa sección"
    raise_exception = True


class EditarCostosView(LoginAndPermissionRequiredMixin, ModalViewMixin, UpdateView):
    permission_required = 'costos.can_manage_costos'
    permission_denied_message = "No posee los permisos suficientes para ingresar a esa sección"
    raise_exception = True
    model = Costo
    # form_class = CostoEditForm

    def get_form_class(self, **kwargs):
        return CostoEditPorCCForm if self.object.tipo_costo.es_por_cc else CostoEditPorEquipoForm

    def get_url_post_form(self):
        return reverse_lazy('costos:costos_edit', args=(self.object.pk, ))

    def get_context_data(self, *args, **kwargs):
        ctx = super(EditarCostosView, self).get_context_data(*args, **kwargs)
        ctx["modal_title"] = 'Editar costo'
        return ctx

    def form_valid(self, form):
        obj = form.save()
        return render(self.request, 'modal_success.html', {'obj': obj})


class EliminarCostosView(LoginAndPermissionRequiredMixin, ModalViewMixin, DeleteView):
    permission_required = 'costos.can_manage_costos'
    permission_denied_message = "No posee los permisos suficientes para ingresar a esa sección"
    raise_exception = True
    # http_method_names = ["post", ]
    model = Costo
    template_name = "modal_delete_form.html"

    def get_url_post_form(self):
        return reverse_lazy('costos:costos_delete', args=(self.object.pk, ))

    def post(self, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return render(self.request, 'modal_delete_success.html', {'obj': obj})


costos_list = CostosList.as_view()
copia_costos = CopiaCostosView.as_view()
costos_alta_cc = CostosAltaCC.as_view()
costos_alta_eq = CostosAltaEquipos.as_view()
costos_select = CargarCostosSelectView.as_view()
costos_edit = EditarCostosView.as_view()
costos_delete = EliminarCostosView.as_view()
