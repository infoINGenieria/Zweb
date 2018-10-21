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
                'valign': 'vcenter',
                'border': 1
            }),
            'header': self.workbook.add_format({
                'bg_color': '#59677e',
                'color': 'white',
                'align': 'left',
                'valign': 'vcenter',
                'border': 1,
                'bold': True,
                'font_size': 10,
            }),
            'header_dest': self.workbook.add_format({
                'bg_color': '#f47c3c',
                'color': 'white',
                'align': 'left',
                'valign': 'vcenter',
                'border': 1,
                'bold': True,
                'font_size': 10,
            }),
            'header_num': self.workbook.add_format({
                'bg_color': '#59677e',
                'color': 'white',
                'align': 'right',
                'valign': 'vcenter',
                'border': 1,
                'bold': True,
                'font_size': 10,
                'num_format': '$ #,##0.00'
            }),
            'header_perc': self.workbook.add_format({
                'bg_color': '#59677e',
                'color': 'white',
                'align': 'right',
                'valign': 'vcenter',
                'border': 1,
                'bold': True,
                'font_size': 10,
                'num_format': '0.0%'
            }),
            'header_date': self.workbook.add_format({
                'bg_color': '#59677e',
                'color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'bold': True,
                'font_size': 10,
                'num_format': 'dd/mm/yy'
            }),
            'normal': self.workbook.add_format({
                'color': 'black',
                'align': 'right',
                'valign': 'vcenter',
                'border': 1,
                'font_size': 9,
            }),
            'normal_left': self.workbook.add_format({
                'color': 'black',
                'align': 'left',
                'valign': 'vcenter',
                'border': 1,
                'font_size': 9,
            }),
            'normal_money': self.workbook.add_format({
                'color': 'black',
                'align': 'right',
                'valign': 'vcenter',
                'border': 1,
                'font_size': 9,
                'num_format': '$ #,##0.00'
            }),
            'normal_date': self.workbook.add_format({
                'color': 'black',
                'align': 'right',
                'valign': 'vcenter',
                'border': 1,
                'font_size': 9,
                'num_format': 'dd/mm/yy'
            }),
            'normal_time': self.workbook.add_format({
                'color': 'black',
                'align': 'right',
                'valign': 'vcenter',
                'border': 1,
                'font_size': 9,
                'num_format': 'hh:ss',
            }),
            'normal_time_dest': self.workbook.add_format({
                'color': 'black',
                'align': 'right',
                'valign': 'vcenter',
                'border': 1,
                'font_size': 9,
                'num_format': 'hh:ss',
                'bg_color': '#faa11c',
            }),
            'normal_perc': self.workbook.add_format({
                'color': 'black',
                'align': 'right',
                'valign': 'vcenter',
                'border': 1,
                'font_size': 9,
                'num_format': '0.0%'
            }),
            'total': self.workbook.add_format({
                'color': 'red',
                'bg_color': 'yellow',
                'align': 'rigth',
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
                    worksheet_s.write(row, i, line[i], self.style_dict["header"] if row in [3, 7] or i == 0 else self.style_dict["normal_money"])
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
        fila_formula = len(context["resumen_costos"]) + row - 1
        for line in context["resumen_costos"]:
            for i in range(0, len(line)):
                if row == fila_formula and i > 0:
                    ws_costos.write_formula(row, i, '=sum({0}{1}:{0}{2})'.format(self.get_c(i + 1), 5, fila_formula),
                                            self.style_dict["header_num"], line[i])
                else:
                    ws_costos.write(row, i, line[i],
                                    self.style_dict["header"] if row in [3, fila_formula] or i == 0 else self.style_dict["normal_money"])
                if row == 3:
                    ws_costos.set_column(row, i, 30)
                else:
                    ws_costos.set_column(row, i, 20)
            row += 1

        ws_costos.set_row(3, 25)
        ws_costos.set_row(fila_formula, 25)
        ws_costos.write_rich_string(row + 1, 0, "TOTAL:", self.style_dict["total_legend"])
        ws_costos.write_formula(row + 1, 1,
                                '=sum({0}{2}:{1}{2})'.format(
                                        self.get_c(2), self.get_c(i + 1), row),
                                self.style_dict["total"], context["total"])
        # añadimos el gráfico
        chart = self.workbook.add_chart({'type': 'column'})
        # Configure the chart. In simplest case we add one or more data series.
        chart.add_series({
            'values': ['Resumen de costos', fila_formula, 1, fila_formula, i],
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
            'values': ['Resumen de costos', fila_formula, 1, fila_formula, i],
            'categories': ['Resumen de costos', 3, 1, 3, i],
            'data_labels': {'percentage': True, 'category':True}
        })
        ws_costos.insert_chart('E17', pie_chart)

    def fill_custom_export(self, context):
        """
        Exporta el panel de control por rango a excel.!
        """
        self.fill_custom_costos_ventas(context)
        self.fill_custom_resumen_costos(context)
        return self.prepare_response()

    def fill_custom_costos_ventas(self, context):
        """
        arma una hoja de calculo con los costso vs ventas como se ve en el panel de control.
        """
        periodos = [x.descripcion for x in context["data"]["periodos"]]
        cert_vs_costos = context["data"]["cert_vs_costos"]
        totales = context["data"]["totales"]
        headers = context["data"]["cc_headers"]

        worksheet_s_name = "Ventas vs Costos"
        worksheet_s = self.workbook.add_worksheet(worksheet_s_name)

        worksheet_s.merge_range('A2:H2', "VENTAS vs COSTOS (Periodos: {})".format(
            " ,".join(periodos)), self.style_dict["title"])

        row = 3
        # cabeceras izquerda
        worksheet_s.set_column(0, 0, 18)  # colum_ini, colun_fin, tamaño
        worksheet_s.set_row(row, 25)
        worksheet_s.write_column(row, 0, ["CC", "Costos", "Certificaciones", "Cert. Internas", "Diferencia"], self.style_dict["header"])

        # completamos datos
        column_num = 1
        for cc_id, datos in cert_vs_costos.items():
            # head
            worksheet_s.write(row, column_num, headers[cc_id], self.style_dict["header"])
            worksheet_s.set_column(column_num, column_num, 22)
            # datos
            i = row + 1
            for costo in ['costos', 'certificaciones', 'certif_internas']:
                worksheet_s.write(i, column_num, datos[costo], self.style_dict["normal_money"])
                i += 1
            # formula
            worksheet_s.write(i, column_num, '=-{0}{1}+{0}{2}+{0}{3}'.format(self.get_c(column_num + 1), 5, 6, 7),
                              self.style_dict["header_num"], datos["diferencia"])
            column_num += 1
        # escribimos formulas de subtotales
        worksheet_s.write(row, column_num, "Subtotales", self.style_dict["header"])
        worksheet_s.set_column(column_num, column_num, 20)
        i = row + 1
        for costo in ['t_costos', 't_certif', 't_servicios', 't_diff']:
            worksheet_s.write_formula(i, column_num,
                                      '=sum({0}{2}:{1}{2})'.format(self.get_c(2), self.get_c(column_num), i + 1),
                                      self.style_dict["header_num"], totales[costo])
            i += 1
        worksheet_s.set_row(7, 25)

        # añadimos el gráfico
        chart = self.workbook.add_chart({'type': 'column'})
        categories = "='{2}'!${0}$4:${1}$4".format(self.get_c(2), self.get_c(column_num), worksheet_s_name)
        chart.add_series({'values': "='{2}'!${0}$5:${1}$5".format(self.get_c(2), self.get_c(column_num), worksheet_s_name),
                          'categories': categories, 'name': 'Costos'})
        chart.add_series({'values': "='{2}'!${0}$6:${1}$6".format(self.get_c(2), self.get_c(column_num), worksheet_s_name),
                          'categories': categories, 'name': "Ventas"})
        chart.add_series({'values': "='{2}'!${0}$7:${1}$7".format(self.get_c(2), self.get_c(column_num), worksheet_s_name),
                          'categories': categories, 'name': 'Certif. Internas'})
        chart.set_x_axis({
            'name': 'Centros de costos',
            'name_font': {'size': 14, 'bold': True},
            'num_font': {'italic': True},

        })
        chart.set_y_axis({'num_format': '$ #,##0.00'})
        chart.set_title({'name': 'Costos vs Ventas'})
        worksheet_s.insert_chart('B10', chart, {'x_scale': 2, 'y_scale': 2.5})

    def fill_custom_resumen_costos(self, context):
        """
        Arma un excel con el resumen de costos como se ve en el panel de control
        """
        periodos = [x.descripcion for x in context["data"]["periodos"]]
        resumen_costos = context["data"]["costos"]
        costos_totales = context["data"]["costos_totales"]
        tipo_costo = context["data"]["costos_headers"]
        headers = context["data"]["cc_headers"]

        ws_costos_name = "Resumen de costos"
        ws_costos = self.workbook.add_worksheet(ws_costos_name)

        ws_costos.merge_range('A2:H2', "RESUMEN DE COSTOS (Periodos: {})".format(
            " ,".join(periodos)), self.style_dict["title"])

        row = 3
        fila_formula = row + len(resumen_costos) - 1
        # cabeceras izquerda
        ws_costos.set_column(0, 0, 18)  # colum_ini, colun_fin, tamaño
        ws_costos.set_row(row, 25)
        ws_costos.write_column(row, 0, ["TIPO DE COSTO"] + list(tipo_costo.values()) + ["Totales"],
                               self.style_dict["header"])
        # completamos datos
        column_num = 1
        i = row + 1
        for cc_id, datos in resumen_costos.items():
            # head
            ws_costos.write(row, column_num, headers[cc_id], self.style_dict["header"])
            ws_costos.set_column(column_num, column_num, 22)
            # datos
            i = row + 1
            for costo in tipo_costo.keys():
                ws_costos.write(i, column_num, datos[costo], self.style_dict["normal_money"])
                i += 1
            # formula
            ws_costos.write(i, column_num, '=sum({0}{1}:{0}{2})'.format(self.get_c(column_num + 1), 5, fila_formula),
                            self.style_dict["header_num"], costos_totales[cc_id])
            column_num += 1
        ws_costos.set_row(fila_formula, 25)

        row = i + 2
        ws_costos.write_rich_string(row + 1, 0, "TOTAL:", self.style_dict["total_legend"])
        ws_costos.write_formula(row + 1, 1, '=sum({0}{2}:{1}{2})'.format(self.get_c(2), self.get_c(column_num), row),
                                self.style_dict["total"], sum(costos_totales.values()))

        # añadimos el gráfico
        chart = self.workbook.add_chart({'type': 'column'})
        # Configure the chart. In simplest case we add one or more data series.
        chart.add_series({
            'values': ['Resumen de costos', fila_formula, 1, fila_formula, column_num - 1],
            'categories': ['Resumen de costos', 3, 1, 3, column_num - 1],
            'name': 'Costos',
            'data_labels': {'value': True, 'num_format': '$ #,##0.00'}
        })

        chart.set_x_axis({
            'name': 'Centros de costos',
            'name_font': {'size': 12, 'bold': True},
            'num_font':  {'italic': True},

        })
        chart.set_y_axis({'num_format': '$ #,##0.00'})
        chart.set_style(21)
        ws_costos.insert_chart('A18', chart, {'x_scale': 1.5, 'y_scale': 2})

        pie_chart = self.workbook.add_chart({'type': 'pie'})
        pie_chart.add_series({
            'values': ['Resumen de costos', fila_formula, 1, fila_formula, column_num - 1],
            'categories': ['Resumen de costos', 3, 1, 3, column_num - 1],
            'data_labels': {'percentage': True, 'category': True}
        })
        ws_costos.insert_chart('F18', pie_chart, {'x_scale': 1.5, 'y_scale': 1.75})
