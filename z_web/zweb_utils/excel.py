import io
import xlsxwriter


class ExportExcelMixin:
    LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def get_c(self, col):

        result = []
        while col:
            col, rem = divmod(col-1, 26)
            result[:0] = self.LETTERS[rem]
        return ''.join(result)

    def __init__(self):
        self.output = io.BytesIO()
        self.workbook = xlsxwriter.Workbook(self.output, {'in_memory': True})
        self.set_default_style()

    def prepare_response(self):
        self.workbook.close()
        xlsx_data = self.output.getvalue()
        # xlsx_data contains the Excel file
        return xlsx_data

    def set_default_style(self):
        self.style_dict = {
            'title': self.workbook.add_format({
                'bold': True,
                'font_size': 14,
                'align': 'center',
                'valign': 'vcenter'
            }),
            'header': self.workbook.add_format({
                'bg_color': '#59677e',
                'color': 'white',
                'align': 'left',
                'valign': 'vcenter',
                'border': 1,
                'bold': True,
                'font_size': 12,
            }),
            'header_num': self.workbook.add_format({
                'bg_color': '#59677e',
                'color': 'white',
                'align': 'right',
                'valign': 'vcenter',
                'border': 1,
                'bold': True,
                'font_size': 12,
                'num_format': '$ #,##0.00'
            }),
            'normal': self.workbook.add_format({
                'color': 'black',
                'align': 'right',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '$ #,##0.00'
            }),
            'total': self.workbook.add_format({
                'color': 'red',
                'bg_color': 'yellow',
                'align': 'left',
                'valign': 'vcenter',
                'border': 2,
                'num_format': '$ #,##0.00'
            }),
            'total_legend': self.workbook.add_format({
                'color': 'red',
                'bg_color': 'yellow',
                'align': 'right',
                'valign': 'vcenter',
                'border': 2,
            }),
        }


class ExportPanelControl(ExportExcelMixin):

    def fill_export(self, context):
        self.fill_costos_ventas_ws(context)
        self.fill_resumen_costos(context)
        return self.prepare_response()

    def fill_costos_ventas_ws(self, context):
        worksheet_s_name = "Ventas vs Costos"
        worksheet_s = self.workbook.add_worksheet(worksheet_s_name)

        worksheet_s.merge_range('A2:F2', "VENTAS vs COSTOS (Periodo: {})".format(context["periodo"]),
                                self.style_dict["title"])
        row = 3
        dict_t = {4: 't_costos', 5: 't_certif', 6: 't_servicios', 7: 't_diff'}
        for line in context["cert_costos"]:
            for i in range(0, len(line)):
                if row == 7 and i > 0:  # a los totales los escribo con formula
                    worksheet_s.write_formula(row, i, '=-{0}{1}+{0}{2}+{0}{3}'.format(self.get_c(i + 1), 5, 6, 7),
                                              self.style_dict["header_num"], line[i])
                else:
                    worksheet_s.write(row, i, line[i], self.style_dict["header"] if row in [3, 7] or i == 0 else self.style_dict["normal"])
                if row == 3:
                    worksheet_s.set_column(row, i, 30)
                else:
                    worksheet_s.set_column(row, i, 20)

            if row == 3:
                worksheet_s.write(row, i + 1, "Subtotales", self.style_dict["header"])
            else:
                worksheet_s.write_formula(row, i + 1, '=sum({0}{2}:{1}{2})'.format(self.get_c(2), self.get_c(i + 1), row + 1), self.style_dict["header_num"],
                                          context["costos_ventas_total"][dict_t[row]])
            worksheet_s.set_column(row, i + 1, 20)
            row+=1
        worksheet_s.set_row(3, 25)
        worksheet_s.set_row(7, 25)

        # añadimos el gráfico
        chart = self.workbook.add_chart({'type': 'column'})
        # Configure the chart. In simplest case we add one or more data series.
        categories = "='{2}'!${0}$4:${1}$4".format(self.get_c(2), self.get_c(i+1), worksheet_s_name)
        chart.add_series({'values': "='{2}'!${0}$5:${1}$5".format(self.get_c(2), self.get_c(i+1), worksheet_s_name),
                          'categories': categories, 'name': 'Costos'})
        chart.add_series({'values': "='{2}'!${0}$6:${1}$6".format(self.get_c(2), self.get_c(i+1), worksheet_s_name),
                          'categories': categories, 'name':"Ventas" })
        chart.add_series({'values': "='{2}'!${0}$7:${1}$7".format(self.get_c(2), self.get_c(i+1), worksheet_s_name),
                          'categories': categories, 'name': 'Certif. Internas' })
        chart.set_x_axis({
            'name': 'Centros de costos',
            'name_font': {'size': 14, 'bold': True},
            'num_font':  {'italic': True },

        })
        chart.set_y_axis({'num_format': '$ #,##0.00'})
        chart.set_title({'name': 'Costos vs Ventas'})
        # Insert the chart into the worksheet.
        worksheet_s.insert_chart('B10', chart, {'x_scale': 2, 'y_scale': 1.5})

    def fill_resumen_costos(self, context):
        ws_costos_name = "Resumen de costos"
        ws_costos = self.workbook.add_worksheet(ws_costos_name)
        ws_costos.merge_range('A2:F2', "Periodo: {}".format(context["periodo"]),
                              self.style_dict["title"])

        row = 3
        for line in context["resumen_costos"]:
            for i in range(0, len(line)):
                if row == 12 and i > 0:
                    ws_costos.write_formula(row, i, '=sum({0}{1}:{0}{2})'.format(self.get_c(i + 1), 5, 12),
                                            self.style_dict["header_num"], line[i])
                else:
                    ws_costos.write(row, i, line[i],
                                    self.style_dict["header"] if row in [3, 12] or i == 0 else self.style_dict["normal"])
                if row == 3:
                    ws_costos.set_column(row, i, 30)
                else:
                    ws_costos.set_column(row, i, 20)
            row += 1

        ws_costos.set_row(3, 25)
        ws_costos.set_row(12, 25)
        ws_costos.write_rich_string(row + 1, 0, "TOTAL:", self.style_dict["total_legend"])
        ws_costos.write_formula(row + 1, 1,
                                '=sum({0}{2}:{1}{2})'.format(
                                        self.get_c(2), self.get_c(i + 1), row),
                                self.style_dict["total"], context["total"])
        # añadimos el gráfico
        chart = self.workbook.add_chart({'type': 'column'})
        # Configure the chart. In simplest case we add one or more data series.
        chart.add_series({
            'values': ['Resumen de costos', 12, 1, 12, i],
            'categories': ['Resumen de costos', 3, 1, 3, i],
            'name': 'Costos',
            'data_labels': {'value': True, 'num_format': '$ #,##0.00'}
        })

        chart.set_x_axis({
            'name': 'Centros de costos',
            'name_font': {'size': 12, 'bold': True},
            'num_font':  {'italic': True },

        })
        chart.set_y_axis({'num_format': '$ #,##0.00'})
        chart.set_style(21)
        # Insert the chart into the worksheet.
        ws_costos.insert_chart('A17', chart, {'x_scale': 1, 'y_scale': 1.5})

        pie_chart = self.workbook.add_chart({'type': 'pie'})
        pie_chart.add_series({
            'values': ['Resumen de costos', 12, 1, 12, i],
            'categories': ['Resumen de costos', 3, 1, 3, i],
            'data_labels': {'percentage': True, 'category':True}
        })
        ws_costos.insert_chart('E17', pie_chart)
