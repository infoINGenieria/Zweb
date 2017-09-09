from django.shortcuts import render

from django.http import HttpResponse
from django.views.generic import TemplateView, FormView

from core.models import Operarios
from reportes.forms import OperarioHorasReporteForm
from reportes.reports import gen_report_detalle_hora
from reportes.excel import ExportToExcel


class ReportesIndexView(TemplateView):
    template_name = 'reportes/base_reportes.html'


class OperarioHoraReporteView(TemplateView):
    template_name = 'reportes/operario_horas_reporte.html'

    def get_context_data(self, **kwargs):
        context = super(OperarioHoraReporteView, self).get_context_data(**kwargs)
        f_filter = OperarioHorasReporteForm(self.request.GET) if self.request.GET else OperarioHorasReporteForm()
        if f_filter.is_valid():
            operarios = Operarios.objects.filter(cct=f_filter.cleaned_data["cct"]).values('pk', 'nombre')
            data = {}
            for operario in operarios:
                data[operario["nombre"]] = gen_report_detalle_hora(
                    operario['pk'], f_filter.cleaned_data["fecha_inicio"],
                    f_filter.cleaned_data["fecha_fin"], f_filter.cleaned_data["cct"])

            # TODO: Realizar reportes para otros CCT
            if f_filter.cleaned_data["cct"].nombre == 'UOCRA':
                context["report"] = data
            else:
                context["empty"] = True
        context["filter"] = f_filter
        return context

    def get(self, request, **kwargs):
        response = super(OperarioHoraReporteView, self).get(request, **kwargs)
        if "report" in response.context_data:
            resp = HttpResponse(content_type='application/vnd.ms-excel')
            resp['Content-Disposition'] = 'attachment; filename=ReporteHorasDetallado.xlsx'
            xlsx_data = ExportToExcel().fill_hora_operario_detalle(response.context_data["report"])
            resp.write(xlsx_data)
            return resp
        return response


reportes_index = ReportesIndexView.as_view()
operario_hora_reporte = OperarioHoraReporteView.as_view()
