from decimal import Decimal as D
from zweb_utils.excel import ExportExcelMixin

from .calculo_costos import get_stats_of_asistencia_by_cc, get_stats_of_asistencia_summary


class ExportReportTaller(ExportExcelMixin):

    def fill_details_of_asistencia(self, details, cc=None):
        """
        Muestra un listado de los dias y el equipo
        """
        worksheet_s_name = "Detalles de asistencia"
        worksheet_s = self.workbook.add_worksheet(worksheet_s_name)
        row = 0
        worksheet_s.write_row(row, 0, ['Día', 'N° Int.', 'Dominio', 'Propio/Alquilado', 'Equipo'], self.style_dict["header_dest"])
        if not cc:
            worksheet_s.write_row(row, 5, ["Unidad de negocio", "Deposito", "Centro de costos"], self.style_dict["header_dest"])

        row += 1
        for asistencia in details.distinct():
            if cc:
                registros = asistencia.registros.filter(centro_costo=cc).order_by('equipo__n_interno').distinct()
            else:
                registros = asistencia.registros.order_by('centro_costo__deposito').distinct()
            for reg in registros:
                worksheet_s.write(row, 0, asistencia.dia, self.style_dict["normal_date"])
                worksheet_s.write(row, 1, reg.equipo.n_interno, self.style_dict["normal"])
                worksheet_s.write(row, 2, reg.equipo.dominio, self.style_dict["normal"])
                worksheet_s.write(row, 3, "Alquilado" if reg.equipo.es_alquilado else "Propio", self.style_dict["normal"])
                worksheet_s.write(row, 4, reg.equipo.equipo, self.style_dict["normal"])
                if not cc:
                    worksheet_s.write(row, 5, reg.centro_costo.unidad_negocio.codigo, self.style_dict["normal"])
                    worksheet_s.write(row, 6, reg.centro_costo.deposito, self.style_dict["normal"])
                    worksheet_s.write(row, 7, reg.centro_costo.obra, self.style_dict["normal"])

                row += 1

        worksheet_s.set_column(0, 3, 15)
        worksheet_s.set_column(4, 4, 25)
        if cc:
            worksheet_s.autofilter('A1:E1')
        else:
            worksheet_s.set_column(5, 6, 15)
            worksheet_s.set_column(7, 7, 30)
            worksheet_s.autofilter('A1:H1')

    def report_asistencia_equipo_summary(self, periodo):
        data, details = get_stats_of_asistencia_summary(periodo)
        worksheet_s_name = "Informe de equipo - resumen"
        worksheet_s = self.workbook.add_worksheet(worksheet_s_name)

        worksheet_s.merge_range(
            'A2:F2',
            "Informe de equipo (Periodo: {})".format(periodo), self.style_dict["title"])

        row = 3
        headers = ["UN", "DEPOSITO", "CENTRO_DE COSTOS", "CONSUMO EQUIPOS PROPIOS", "CONSUMO EQUIPOS ALQUILADOS"]
        worksheet_s.write_row(row, 0, headers, self.style_dict["header_dest"])

        row += 1
        total_propio = D(0)
        total_alquilado = D(0)
        for cc_id, row_data in data.items():
            """
            {
                5:
                {
                    'centro_costo': <Obras: Gerencia de Mov de Suelos - 1200000003 - Gerencia de Movimiento de Suelos>,
                    'consumo_propios': Decimal('9637.409523809523809523809524'),
                    'un': 'MS'
                },
            }
            """
            cc = row_data["centro_costo"]
            worksheet_s.write(row, 0, row_data["un"], self.style_dict["normal_left"])
            worksheet_s.write(row, 1, cc.deposito, self.style_dict["normal_left"])
            worksheet_s.write(row, 2, cc.obra, self.style_dict["normal_left"])
            total_propio += row_data.get('consumo_propios', 0)
            total_alquilado += row_data.get('consumo_alquilados', 0)
            worksheet_s.write(row, 3, row_data.get('consumo_propios', 0), self.style_dict["normal_money"])
            worksheet_s.write(row, 4, row_data.get('consumo_alquilados', 0), self.style_dict["normal_money"])
            row += 1

        # Total
        worksheet_s.write_formula(row, 3, '=sum({0}5:{0}{1})'.format(self.get_c(4), len(data) + 5 - 1), self.style_dict["total"], total_propio)
        worksheet_s.write_formula(row , 4, '=sum({0}5:{0}{1})'.format(self.get_c(5), len(data) + 5 - 1), self.style_dict["total"], total_alquilado)
        worksheet_s.set_column(0, 1, 8)
        worksheet_s.set_column(2, 2, 35)
        worksheet_s.set_column(3, 4, 26)

        self.fill_details_of_asistencia(details)
        return self.prepare_response()

    def report_asistencia_equipo_by_cc(self, periodo, centro_costo):
        data, details = get_stats_of_asistencia_by_cc(periodo, centro_costo.pk)
        worksheet_s_name = "Informe de equipo"
        worksheet_s = self.workbook.add_worksheet(worksheet_s_name)

        worksheet_s.merge_range(
            'A2:H2',
            "Informe de equipo: {} (Periodo: {})".format(
                centro_costo, periodo),
            self.style_dict["title"])

        row = 3
        headers = ["Nº Int.", "DOMINIO", "PROPIO / ALQUILADO", "EQUIPO", "DÍAS", "Costo HS", "Costo Diario", "Total"]
        worksheet_s.write_row(row, 0, headers, self.style_dict["header_dest"])

        row += 1
        total = D(0)
        for row_data in data:
            """
            {'centro_costo': <Obras: OS-MEDANITO - OBRA DE SUPERFICIE>,
            'centro_costo_id': 17,
            'costo_diario': Decimal('6179.040952380952380952380954'),
            'costo_hs': Decimal('1029.840158730158730158730159'),
            'dias': 1,
            'equipo': <Equipos: EV 122 - TOPADORA>,
            'equipo_id': 8,
            'horas': 6}
            """
            equipo = row_data["equipo"]
            worksheet_s.write(row, 0, equipo.n_interno, self.style_dict["normal"])
            worksheet_s.write(row, 1, equipo.dominio, self.style_dict["normal"])
            worksheet_s.write(row, 2, "Alquilado" if equipo.es_alquilado else "Propio", self.style_dict["normal_left"])
            worksheet_s.write(row, 3, equipo.equipo, self.style_dict["normal_left"])
            worksheet_s.write(row, 4, row_data["dias"], self.style_dict["normal"])
            worksheet_s.write(row, 5, row_data["costo_hs"], self.style_dict["normal_money"])
            worksheet_s.write(row, 6, row_data["costo_diario"], self.style_dict["normal_money"])
            total_costo = row_data["dias"] * row_data["costo_diario"]
            total += total_costo
            worksheet_s.write_formula(row, 7, '=+{1}{0}*{2}{0}'.format(row + 1, self.get_c(5), self.get_c(7)), self.style_dict["normal_money"], total_costo)
            row += 1

        # Total
        worksheet_s.write_formula(row, 7, '=sum({0}5:{0}{1})'.format(self.get_c(8), len(data) + 5 - 1), self.style_dict["total"], total)
        worksheet_s.set_column(0, 1, 15)
        worksheet_s.set_column(2, 3, 25)
        worksheet_s.set_column(4, 7, 15)

        self.fill_details_of_asistencia(details, centro_costo)
        return self.prepare_response()
