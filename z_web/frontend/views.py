from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from parametros.models import Periodo
from costos.models import CostoParametro, ArchivosAdjuntosPeriodo
from registro.models import Certificacion, AjusteCombustible
from zweb_utils.views import LoginAndPermissionRequiredMixin, LoginRequiredMixin
from .stats import get_utilizacion_equipo, get_cc_on_periodo, get_ventas_costos

from zweb_utils.excel import ExportPanelControl


class Index(LoginRequiredMixin, TemplateView):
    template_name = 'frontend/index.html'


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
            periodo = periodos[0] if periodos else None
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
                                           "periodo {}".format(reverse('admin:registro_certificacion_changelist'), periodo)))
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


index = Index.as_view()
ms_panel_control = MSPanelControl.as_view()
ms_export_panel_control_excel = MSExportarPanel2Excel.as_view()
