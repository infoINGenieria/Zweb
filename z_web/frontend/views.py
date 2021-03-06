from decimal import Decimal as D

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView, RedirectView
from django.utils.timezone import now

from core.models import Obras
from frontend.forms import CustomPanelControlForm
from parametros.models import Periodo
from costos.models import CostoParametro, ArchivosAdjuntosPeriodo
from registro.models import Certificacion
from zweb_utils.views import LoginAndPermissionRequiredMixin, LoginRequiredMixin
from .stats import get_utilizacion_equipo, get_cc_on_periodo, get_ventas_costos, get_headers_costos

from zweb_utils.excel import ExportPanelControl


class Index(LoginRequiredMixin, RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('frontend:ng_index')


class MSPanelControl(LoginAndPermissionRequiredMixin, TemplateView):
    template_name = "frontend/movimiento_suelo/panel_control.html"
    permission_required = 'costos.can_view_panel_control'
    permission_denied_message = "No posee los permisos suficientes para ingresar a esa sección"
    raise_exception = True

    def get_context_data(self, periodos, **kwargs):
        context = super(MSPanelControl, self).get_context_data(**kwargs)
        context["periodos"] = periodos
        if 'periodo' in self.request.GET:
            periodo = Periodo.objects.get(pk=self.request.GET["periodo"])
        else:
            today = now()
            periodo = periodos.filter(fecha_fin__lt=today).first()
        context["periodo"] = periodo
        try:
            context["equipos"], context["totales"] = get_utilizacion_equipo(periodo)
            context["resumen_costos"], context["total"], totales_costos = get_cc_on_periodo(periodo, context["totales"])
            context["cert_costos"], context["costos_ventas_total"] = get_ventas_costos(periodo, totales_costos)
            context["archivos"] = ArchivosAdjuntosPeriodo.objects.filter(periodo=periodo)
        except CostoParametro.DoesNotExist as e:
            messages.add_message(self.request, messages.WARNING,
                                 mark_safe("No están definidos los <a href='/costos/costoparametro'>parámetros de costos</a> para el "
                                           "periodo {}".format(periodo)))
        except Certificacion.DoesNotExist as e:
            messages.add_message(self.request, messages.WARNING,
                                 mark_safe("No hay <a href='{}'>certificaciones de obras</a> para el "
                                           "periodo {}".format('/~/certificaciones/nuevo', periodo)))
        return context

    def get(self, request, *args, **kwargs):
        context = {}
        periodos = Periodo.objects.all().order_by('-fecha_inicio')
        if periodos:
            context = self.get_context_data(periodos)
        else:
            messages.add_message(request, messages.WARNING, "No hay periodos definidos en el sistema.")
        return self.render_to_response(context)


class MSExportarPanel2Excel(MSPanelControl):
    permission_required = ('costos.can_view_panel_control', 'costos.can_export_panel_control', )

    def get(self, request, *args, **kwargs):
        periodos = Periodo.objects.all().order_by('-fecha_inicio')
        if periodos:
            context = self.get_context_data(periodos)
            if 'cert_costos' in context:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
                xlsx_data = ExportPanelControl().fill_export(context)
                response.write(xlsx_data)
                return response
        else:
            messages.add_message(request, messages.WARNING, "No hay periodos definidos en el sistema.")
        return HttpResponseRedirect(reverse("frontend:ms_panel_control"))


class MSCustomPanelControl(LoginAndPermissionRequiredMixin, TemplateView):
    template_name = "frontend/movimiento_suelo/custom_panel_control.html"
    permission_required = 'costos.can_view_panel_control'
    permission_denied_message = "No posee los permisos suficientes para ingresar a esa sección"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(MSCustomPanelControl, self).get_context_data(**kwargs)
        if self.request.GET.get("filtered", False):
            form = CustomPanelControlForm(data=self.request.GET)
        else:
            form = CustomPanelControlForm()
        if form.is_valid():
            context["data"] = self.get_report(form, no_show_message=kwargs.get('no_show_message', False))
        context["form"] = form
        return context

    def get_report(self, form, no_show_message=False):
        """
        Este reporte utiliza los métodos actuales del panel de control, pero limitando las centros de costos, para varios
        periodos.
        """
        cc_id = None
        if form.cleaned_data["centro_costos"]:
            cc_id = form.cleaned_data["centro_costos"].values_list('pk', flat=True)
        if form.cleaned_data["periodo_fin"]:
            periodos = list(Periodo.objects.filter(
                fecha_inicio__gte=form.cleaned_data["periodo_ini"].fecha_inicio,
                fecha_fin__lte=form.cleaned_data["periodo_fin"].fecha_fin).order_by('fecha_inicio'))
        else:
            periodos = [form.cleaned_data["periodo_ini"], ]

        data_costos, data_costos_totales = {}, {}
        data_cert_costos, data_totales = {}, {}

        for periodo in periodos:
            try:
                _, equipos_totales = get_utilizacion_equipo(periodo, limit_cc=cc_id)
                costos, totales_costos = get_cc_on_periodo(periodo, equipos_totales, get_dict=True, limit_cc=cc_id)
                cert_costos, totales = get_ventas_costos(periodo, totales_costos, get_dict=True)  # totales_costos ya está limitado en CC

                self.update_values(data_costos, costos)
                self.update_values(data_costos_totales, totales_costos)
                self.update_values(data_cert_costos, cert_costos)
                self.update_values(data_totales, totales)
            except CostoParametro.DoesNotExist as e:
                if not no_show_message:
                    messages.add_message(
                        self.request, messages.WARNING, mark_safe(
                            "No están definidos los <a href='/admin/costos/costoparametro'>parámetros de costos</a> para el "
                            "periodo <strong>{}</strong>. Se ignora el periodo.".format(periodo)))
            except Certificacion.DoesNotExist as e:
                if not no_show_message:
                    messages.add_message(self.request, messages.WARNING, mark_safe(
                        "No hay <a href='{}'>certificaciones de obras</a> para el "
                        "periodo <strong>{}</strong>. Se ignora el periodo.".format("/~/certificaciones/nuevo", periodo)))
        data_costos, header_costos = self.remove_zero_values(data_costos)
        cc_headers = dict(Obras.objects.filter(es_cc=True, pk__in=data_cert_costos.keys()).values_list('pk', 'codigo'))
        return {
            'costos': data_costos, 'costos_totales': data_costos_totales,
            'cert_vs_costos': data_cert_costos, 'totales': data_totales,
            'cc_headers': cc_headers, 'costos_headers': header_costos,
            'periodos': periodos
        }

    def remove_zero_values(self, costos):
        """
        Calculo los totales de cada items, y si este es 0,
        remuevo esos datos junto a la cabecera correspondiente.
        """
        headers = dict(get_headers_costos())

        suma = dict()
        for head in headers.keys():
            for key in costos.keys():
                suma[head] = suma.get(head, 0) + costos[key].get(head)
        for key, _suma in suma.items():
            if _suma == 0:
                del headers[key]
                for _id in costos.keys():
                    del costos[_id][key]
        return costos, headers

    def update_values(self, data, values):
        """
        Suma valores de distintos periodos si coinciden en obra y tipo
        :param data: data acumulada
        :param values: data de este periodo
        :return: la data acumulada.
        """
        for cc_id, vals in values.items():
            if cc_id not in data:
                data[cc_id] = vals
            else:
                if isinstance(vals, (float, int, D)):
                    data[cc_id] += vals
                else:
                    for costo, val in vals.items():
                        if costo in data[cc_id]:
                            data[cc_id][costo] = data[cc_id][costo] + val
                        else:
                            data[cc_id][costo] = val
        return data


class MSExportarCustomPanel2Excel(MSCustomPanelControl):
    permission_required = ('costos.can_view_panel_control', 'costos.can_export_panel_control', )

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(no_show_message=True)
        if 'data' in context:
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
            xlsx_data = ExportPanelControl().fill_custom_export(context)
            response.write(xlsx_data)
            return response
        return self.render_to_response(context)


class NgIndex(LoginRequiredMixin, TemplateView):
    template_name = 'frontend/ng_base.html'


# Angular app
ng_index = NgIndex.as_view()

index = Index.as_view()
ms_panel_control = MSPanelControl.as_view()
ms_export_panel_control_excel = MSExportarPanel2Excel.as_view()
ms_custom_panel_control = MSCustomPanelControl.as_view()
ms_export_custom_panel_control_excel = MSExportarCustomPanel2Excel.as_view()

