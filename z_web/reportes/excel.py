# coding: utf-8
import io
import os
import xlsxwriter
from datetime import datetime
from collections import Counter

from django.conf import settings

from zweb_utils.dates import daterange


class ExportExcelMixin:
    LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def get_c(self, col):
        """ Convert given row and column number to an Excel-style cell name. """
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
