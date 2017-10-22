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
from .models import (CostoParametro, Costo, CostoTipo, CostoProyeccion, CostoReal,
                     AvanceObraReal, AvanceObraProyeccion, AvanceObra)
from .forms import (CostoItemForm, CostoItemFamiliaForm,
                    CopiaCostoForm, CostoCCForm, PeriodoCCForm, PeriodoCostoTipoForm,
                    CostoEquipoForm, CostoEditPorCCForm, CostoEditPorEquipoForm,
                    ProyeccionEditPorCCForm, ProyeccionEditPorEquipoForm,
                    AvanceObraEditForm, AvanceObraProyectadoEditForm,
                    CentroCostoSelectForm, AvanceObraCreateForm)
from .tables import (CostoTableGeneric, CostosByCCTotalTable,
                     CostosByEquipoMontoHSTable, ProyeccionTableGeneric,
                     ProyeccionByCCTotalTable, ProyeccionByEquipoMontoHSTable,
                     AvanceObraProyeccionTable, AvanceObraRealTable)
from .filters import CostosFilter, AvanceObraFilter


class BaseCostosMixin(LoginAndPermissionRequiredMixin):
    permission_required = 'costos.can_manage_costos'
    permission_denied_message = "No posee los permisos suficientes para ingresar a esa sección"
    raise_exception = True


class FormWithUserMixin(object):

    def get_form_kwargs(self):
        kwargs = super(FormWithUserMixin, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class CostosIndexView(BaseCostosMixin, TemplateView):
    template_name = "frontend/costos/base_costos.html"


class CopiaCostosView(BaseCostosMixin, TemplateView):
    """
    Vista para copiar costos de un periodo a otro.
    """
    template_name = "frontend/costos/copiar_costos.html"

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


class CostosList(BaseCostosMixin, TableFilterListView):
    template_name = 'frontend/costos/costo_list.html'
    filterset_class = CostosFilter
    model = CostoReal

    def get_filterset(self, *args, **kwargs):
        """
        Solo mostramos centro de costos de la unidad de negocio del usuario
        """
        fs = super(CostosList, self).get_filterset(*args, **kwargs)
        fs.filters['centro_costo'].field.queryset = Obras.get_centro_costos(self.request.user)
        return fs

    def get_queryset(self):
        return CostoReal.objects.filter(
            centro_costo__in=Obras.get_centro_costos(self.request.user))

    def get_table_class(self, **kwargs):
        if self.filterset.form.is_valid():
            tipo_costo = self.filterset.form.cleaned_data["tipo_costo"]
            relacionado_con = self.filterset.form.cleaned_data["relacionado_con"]
            if tipo_costo:
                return CostosByCCTotalTable if tipo_costo.es_por_cc else CostosByEquipoMontoHSTable
            if relacionado_con:
                return CostosByCCTotalTable if relacionado_con == 'cc' else CostosByEquipoMontoHSTable

        return CostoTableGeneric

    def get_context_data(self, **kwargs):
        ctx = super(CostosList, self).get_context_data(**kwargs)
        ctx["is_filtered"] = self.filterset.form.is_valid()
        return ctx


class CostosAltaCC(BaseCostosMixin, TemplateView):
    model = CostoReal
    template_name = "frontend/costos/costos_cc_form.html"

    def _form_class(self):
        return PeriodoCCForm

    def _get_formset(self):
        return formset_factory(CostoCCForm, extra=0)

    def get_context_data(self, **kwargs):
        context = super(CostosAltaCC, self).get_context_data(**kwargs)
        context["tipos_costos"] = self.get_queryset()
        if "p_form" not in kwargs:
            context["p_form"] = self._form_class()(self.request.user)
        if "formsets" not in kwargs:
            Formset = self._get_formset()
            initial = [{'tipo_costo': x.pk} for x in context["tipos_costos"]]
            context["formsets"] = Formset(initial=initial)
        return context

    def get_queryset(self, **kwargs):
        return CostoTipo.objects.filter(relacionado_con='cc')

    def post(self, request, *args, **kwargs):
        p_form = self._form_class()(self.request.user, self.request.POST)
        formsets = self._get_formset()(self.request.POST)

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
                        if self.model.objects.filter(
                            periodo=periodo, centro_costo=centro_costo, tipo_costo=tipo_costo).exists():
                            errors = f._errors.setdefault("monto_total", ErrorList())
                            errors.append(u"Ya existe un valor para el periodo y centro de costo seleccionado.")
                            has_error = True
                        else:
                            costo = self.model(**f.cleaned_data)
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


class CostosAltaEquipos(BaseCostosMixin, TemplateView):
    template_name = "frontend/costos/costos_eq_form.html"
    form_class = CostoItemForm
    model = CostoProyeccion

    def _form_class(self):
        return PeriodoCostoTipoForm

    def _get_formset(self):
        return formset_factory(CostoEquipoForm, extra=0)

    def get_context_data(self, **kwargs):
        context = super(CostosAltaEquipos, self).get_context_data(**kwargs)
        context["familias"] = self.get_queryset()
        if "p_form" not in kwargs:
            context["p_form"] = self._form_class()()
        if "formsets" not in kwargs:
            Formset = self._get_formset()
            initial = [{'familia_equipo': x.pk} for x in context["familias"]]
            context["formsets"] = Formset(initial=initial)
        return context

    def get_queryset(self, **kwargs):
        return FamiliaEquipo.objects.all()

    def post(self, request, *args, **kwargs):
        p_form = self._form_class()(self.request.POST)
        formsets = self._get_formset()(self.request.POST)

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
                        if self.model.objects.filter(
                            periodo=periodo, familia_equipo=familia, tipo_costo=tipo_costo).exists():
                            errors = f._errors.setdefault("monto_hora", ErrorList())
                            errors.append(u"Ya existe un valor para el periodo y familia de equipos seleccionado.")
                            has_error = True
                        else:
                            costo = self.model(**f.cleaned_data)
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


class CargarCostosSelectView(BaseCostosMixin, TemplateView):
    template_name = 'frontend/costos/modal/cargar_costos_select.html'

    def get_context_data(self, **kwargs):
        context = super(CargarCostosSelectView, self).get_context_data(**kwargs)
        context["es_proyeccion"] = kwargs.get("es_proyeccion", False)
        return context


class EditarCostosView(BaseCostosMixin, FormWithUserMixin, ModalViewMixin, UpdateView):
    model = CostoReal

    def get_form_class(self, **kwargs):
        return CostoEditPorCCForm if self.object.tipo_costo.es_por_cc else CostoEditPorEquipoForm

    def get_url_post_form(self):
        return reverse_lazy('costos:costos_edit', args=(self.object.pk, ))

    def get_context_data(self, *args, **kwargs):
        ctx = super(EditarCostosView, self).get_context_data(*args, **kwargs)
        ctx["modal_title"] = 'Editar %s' % self.model._meta.verbose_name
        return ctx

    def form_valid(self, form):
        obj = form.save()
        return render(self.request, 'modal_success.html', {'obj': obj})


class EliminarCostosView(BaseCostosMixin, ModalViewMixin, DeleteView):
    # http_method_names = ["post", ]
    model = CostoReal
    template_name = "modal_delete_form.html"

    def get_url_post_form(self):
        return reverse_lazy('costos:costos_delete', args=(self.object.pk, ))

    def post(self, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return render(self.request, 'modal_delete_success.html', {'obj': obj})


################
# PROYECCIONES #
################


class CostosProyeccionListView(CostosList):
    model = CostoProyeccion
    # context_object_name = 'proyecciones'
    template_name = 'frontend/costos/proyeccion_list.html'

    def get_table_class(self, **kwargs):
        if self.filterset.form.is_valid():
            tipo_costo = self.filterset.form.cleaned_data["tipo_costo"]
            relacionado_con = self.filterset.form.cleaned_data["relacionado_con"]
            if tipo_costo:
                return ProyeccionByCCTotalTable if tipo_costo.es_por_cc else ProyeccionByEquipoMontoHSTable
            if relacionado_con:
                return ProyeccionByCCTotalTable if relacionado_con == 'cc' else ProyeccionByEquipoMontoHSTable

        return ProyeccionTableGeneric

    def get_queryset(self):
        return CostoProyeccion.objects.filter(
            centro_costo__in=Obras.get_centro_costos(self.request.user))


class CostosProyeccionAltaCC(CostosAltaCC):
    model = CostoProyeccion
    template_name = "frontend/costos/proyeccion_cc_form.html"

    def response_result(self, p_form, formsets, saved_count):
        if saved_count:
            messages.add_message(
                self.request, messages.SUCCESS,
                "Se añadieron correctamente {} proyecciones al centro de costos '{}' para el periodo '{}'".format(
                    saved_count, p_form.cleaned_data["centro_costo"], p_form.cleaned_data["periodo"]))
            return HttpResponseRedirect(reverse('costos:proyecciones_alta_cc'))
        else:
            messages.add_message(self.request, messages.WARNING, "No íngresó valores de costos")
            return self.form_invalid(p_form, formsets)


class CostosProyeccionAltaEquipos(CostosAltaEquipos):
    model = CostoProyeccion
    template_name = "frontend/costos/proyeccion_eq_form.html"

    def response_result(self, p_form, formsets, saved_count):
        if saved_count:
            messages.add_message(
                self.request, messages.SUCCESS,
                "Se añadieron correctamente {} proyecciones de costos del tipo '{}' para el periodo '{}'".format(
                    saved_count, p_form.cleaned_data["tipo_costo"], p_form.cleaned_data["periodo"]))
            return HttpResponseRedirect(reverse('costos:proyecciones_alta_eq'))
        else:
            messages.add_message(self.request, messages.WARNING, "No íngresó valores de costos")
            return self.form_invalid(p_form, formsets)


class EditarProyeccionesView(EditarCostosView, UpdateView):
    model = CostoProyeccion

    def get_form_class(self, **kwargs):
        return ProyeccionEditPorCCForm if self.object.tipo_costo.es_por_cc else ProyeccionEditPorEquipoForm

    def get_url_post_form(self):
        return reverse_lazy('costos:proyecciones_edit', args=(self.object.pk, ))


class EliminarProyeccionesView(EliminarCostosView):
    model = CostoProyeccion

    def get_url_post_form(self):
        return reverse_lazy('costos:proyecciones_delete', args=(self.object.pk, ))


##################
# AVANCE DE OBRA #
##################


class AvanceObraRealList(BaseCostosMixin, TableFilterListView):
    template_name = 'frontend/costos/avance_obra_list.html'
    filterset_class = AvanceObraFilter
    model = AvanceObraReal
    table_class = AvanceObraRealTable

    def get_filterset(self, *args, **kwargs):
        """
        Solo mostramos centro de costos de la unidad de negocio del usuario
        """
        fs = super(AvanceObraRealList, self).get_filterset(*args, **kwargs)
        fs.filters['centro_costo'].field.queryset = Obras.get_centro_costos(self.request.user)
        return fs

    def get_context_data(self, **kwargs):
        ctx = super(AvanceObraRealList, self).get_context_data(**kwargs)
        ctx["is_filtered"] = self.filterset.form.is_valid()
        return ctx

    def get_queryset(self):
        return self.model.objects.filter(
            centro_costo__in=Obras.get_centro_costos(self.request.user))


class AvanceObraEditView(BaseCostosMixin, FormWithUserMixin, ModalViewMixin, UpdateView):
    model = AvanceObraReal
    form_class = AvanceObraEditForm

    def get_url_post_form(self):
        return reverse_lazy('costos:avances_obra_edit', args=(self.object.pk, ))

    def get_context_data(self, *args, **kwargs):
        ctx = super(AvanceObraEditView, self).get_context_data(*args, **kwargs)
        ctx["modal_title"] = 'Editar %s' % self.model._meta.verbose_name
        return ctx

    def form_valid(self, form):
        obj = form.save()
        return render(self.request, 'modal_success.html', {'obj': obj})


class AvanceObraDeleteView(BaseCostosMixin, ModalViewMixin, DeleteView):
    model = AvanceObraReal
    template_name = "modal_delete_form.html"

    def get_url_post_form(self):
        return reverse_lazy('costos:avances_obra_delete', args=(self.object.pk, ))

    def post(self, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return render(self.request, 'modal_delete_success.html', {'obj': obj})


class AvanceObraCreateView(BaseCostosMixin, TemplateView):
    model = AvanceObra
    template_name = "frontend/costos/avance_obra_create.html"
    form_class = CentroCostoSelectForm
    formset_avance = formset_factory(AvanceObraCreateForm, extra=0, min_num=1, can_delete=True, validate_min=True)
    es_proyeccion = False

    def get_context_data(self, **kwargs):
        context = super(AvanceObraCreateView, self).get_context_data(**kwargs)
        forms = {
            "obra_form": CentroCostoSelectForm(user=self.request.user, prefix='obra_form'),
            "avances_formset": self.formset_avance(prefix='avances_formset'),
        }
        forms.update(context)
        return forms

    def post(self, request, *args, **kwargs):
        obra_form = CentroCostoSelectForm(user=self.request.user, data=self.request.POST, prefix='obra_form')
        avances_formset = self.formset_avance(self.request.POST, prefix='avances_formset')

        if obra_form.is_valid() and avances_formset.is_valid():
            return self.form_valid(obra_form, avances_formset)
        else:
            return self.form_invalid(obra_form, avances_formset)

    def form_invalid(self, obra_form, avances_formset):
        return self.render_to_response(self.get_context_data(obra_form=obra_form, avances_formset=avances_formset))

    def form_valid(self, obra_form, avances_formset):
        has_error = False
        centro_costo = obra_form.cleaned_data["centro_costo"]
        try:
            with atomic():
                for f in avances_formset.forms:
                    if f in avances_formset.deleted_forms:
                        continue
                    if self.model.objects.filter(periodo=f.cleaned_data["periodo"], centro_costo=centro_costo,
                                                 es_proyeccion=self.es_proyeccion).exists():
                        errors = f._errors.setdefault("avance", ErrorList())
                        errors.append(u"Ya existe un valor para el periodo y centro de costo seleccionado.")
                        has_error = True
                    else:
                        f.save(centro_costo, self.es_proyeccion)
                if has_error:
                    raise IntegrityError
        except IntegrityError:
            return self.form_invalid(obra_form, avances_formset)

        return HttpResponseRedirect(self.get_success_url(centro_costo))

    def get_success_url(self, centro_costo):
        messages.success(self.request, "Avances de {} guardados correctamente.".format(centro_costo))
        return reverse_lazy('costos:avances_obra_list')


##################################
# PROYECCIONES DE AVANCE DE OBRA #
##################################

class AvanceObraProyeccionList(AvanceObraRealList):
    model = AvanceObraProyeccion
    table_class = AvanceObraProyeccionTable
    template_name = 'frontend/costos/avance_obra_proyeccion_list.html'


class AvanceObraProyeccionEditView(AvanceObraEditView):
    model = AvanceObraProyeccion
    form_class = AvanceObraProyectadoEditForm

    def get_url_post_form(self):
        return reverse_lazy('costos:avances_obra_proyeccion_edit', args=(self.object.pk, ))


class AvanceObraProyeccionDeleteView(AvanceObraDeleteView):
    model = AvanceObraProyeccion

    def get_url_post_form(self):
        return reverse_lazy('costos:avances_obra_proyeccion_delete', args=(self.object.pk, ))


class AvanceObraProyeccionCreateView(AvanceObraCreateView):
    model = AvanceObraProyeccion
    es_proyeccion = True
    template_name = "frontend/costos/avance_obra_proyeccion_create.html"

    def get_success_url(self, centro_costo):
        messages.success(self.request, "Proyecciones de avances de {} guardados correctamente.".format(centro_costo))
        return reverse_lazy('costos:avances_obra_proyeccion_list')


costos_index = CostosIndexView.as_view()
costos_list = CostosList.as_view()
copia_costos = CopiaCostosView.as_view()
costos_alta_cc = CostosAltaCC.as_view()
costos_alta_eq = CostosAltaEquipos.as_view()
costos_select = CargarCostosSelectView.as_view()
costos_edit = EditarCostosView.as_view()
costos_delete = EliminarCostosView.as_view()
proyecciones_list = CostosProyeccionListView.as_view()
proyecciones_alta_cc = CostosProyeccionAltaCC.as_view()
proyecciones_alta_eq = CostosProyeccionAltaEquipos.as_view()
proyecciones_edit = EditarProyeccionesView.as_view()
proyecciones_delete = EliminarProyeccionesView.as_view()
avances_obra_list = AvanceObraRealList.as_view()
avances_obra_edit = AvanceObraEditView.as_view()
avances_obra_delete = AvanceObraDeleteView.as_view()
avances_obra_create = AvanceObraCreateView.as_view()
avances_obra_proyeccion_list = AvanceObraProyeccionList.as_view()
avances_obra_proyeccion_edit = AvanceObraProyeccionEditView.as_view()
avances_obra_proyeccion_delete = AvanceObraProyeccionDeleteView.as_view()
avances_obra_proyeccion_create = AvanceObraProyeccionCreateView.as_view()
