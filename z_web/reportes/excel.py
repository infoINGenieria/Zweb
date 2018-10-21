# coding: utf-8
import io
import os
import xlsxwriter
from datetime import datetime
from collections import Counter

from django.conf import settings

from zweb_utils.dates import daterange
from zweb_utils.excel import ExportExcelMixin


class ExportToExcel(ExportExcelMixin):

    def fill_hora_operario_detalle(self, data):
        """
        Genera un excel con el informe sobre las horas trabajadas en un rango de fechas dadas.
        Se genera una pestaña por operario.

        """
        for operario, datos in data.items():
            worksheet_s = self.workbook.add_worksheet(operario)

            row = 0
            for item in datos:
                if row == 0:
                    worksheet_s.write_row(row, 0, item[0:2], self.style_dict["header"])
                    worksheet_s.write_row(row, 2, item[2:8], self.style_dict["header_dest"])
                    worksheet_s.write_row(row, 8, item[8:], self.style_dict["header"])

                else:
                    worksheet_s.write_row(row, 0, item[0:2], self.style_dict["normal_time"])
                    worksheet_s.write_row(row, 2, item[2:8], self.style_dict["normal_time_dest"])
                    worksheet_s.write_row(row, 8, item[8:], self.style_dict["normal_time"])

                row += 1
            # worksheet_s.autofilter('A1:A1')
            # worksheet_s.freeze_panes(1, 1)
        return self.prepare_response()
