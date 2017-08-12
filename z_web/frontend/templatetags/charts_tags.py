from django.template.defaulttags import register


@register.inclusion_tag("frontend/tags/resumen_costo_pie.html")
def resumen_costo_pie(data_dict, width=500, height=500):
    data = {}
    if data_dict:
        xdata = data_dict[0][1:]
        ydata = data_dict[-1:][0][1:]
        extra_serie = {"tooltip": {"y_start": "$ ", "y_end": ""}}
        chartdata = {'x': xdata, 'y': ydata, 'extra': extra_serie}
        charttype = "pieChart"
        chartcontainer = 'piechart_container'
        data = {
            'charttype': charttype,
            'chartdata': chartdata,
            'chartcontainer': chartcontainer,
            'extra': {
                'x_is_date': False,
                'x_axis_format': '',
                'tag_script_js': True,
                'jquery_on_ready': False,
            },

        }
    return {
        'data': data,
        'width': width,
        'height': height
    }


@register.inclusion_tag("frontend/tags/resumen_costo_bar.html")
def resumen_costo_bar(data_dict, width=500, height=400):
    data = {}
    if data_dict:
        xdata = data_dict[0][1:]
        ydata = data_dict[-1:][0][1:]
        extra_serie = {"tooltip": {"y_start": "$ ", "y_end": ""}}
        chartdata = {'x': xdata, 'y': ydata, 'extra': extra_serie}
        charttype = "discreteBarChart"
        chartcontainer = 'barchart_container'
        data = {
            'charttype': charttype,
            'chartdata': chartdata,
            'chartcontainer': chartcontainer,
            'extra': {
                'x_is_date': False,
                'x_axis_format': '',
                'tag_script_js': True,
                'jquery_on_ready': False,
                'show_labels': False,
                'show_legend': False,
                'margin_left': 80
            },

        }
    return {
        'data': data,
        'width': width,
        'height': height
    }


@register.filter
def extraer_data_grafico_costos(data_dict, row):
    l_data = list(zip(data_dict[0][1:], data_dict[row:][0][1:]))
    return l_data


@register.filter
def extraer_data_grafico_resumen(data_dict, row):
    l_data = list(zip(data_dict[0][1:], data_dict[row:][0][1:]))
    return l_data


@register.filter
def gen_data_grafico_costos_from_dict(data_dict, cc_headers):
    l = [(cc_headers.get(k), v) for k, v in data_dict.items()]
    return l


@register.filter
def gen_data_grafico_ventas_from_dict(data_dict, cc_headers):
    l = [(cc_headers.get(k), v['certificaciones']) for k, v in data_dict.items()]
    return l


@register.filter
def gen_data_grafico_servicios_from_dict(data_dict, cc_headers):
    l = [(cc_headers.get(k), v['certif_internas']) for k, v in data_dict.items()]
    return l