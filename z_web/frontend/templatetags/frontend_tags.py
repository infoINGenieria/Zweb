from django.template.defaulttags import register

from zweb_utils.format import currency_format, decimal_format, number_js_format


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def money(val):
    try:
        return currency_format(val)
    except TypeError:
        return currency_format(0)


@register.filter
def js_format(val):
    return number_js_format(val)


@register.filter
def obra_codigo(obras, form):
    try:
        if form.initial:
            return "{}".format(obras.get(pk=form.initial["obra"]))
        else:
            return "{}".format(obras.get(pk=form.cleaned_data["obra"].pk))
    except:
        return ""


@register.filter
def nombre_familia(familias, form):
    try:
        if form.initial:
            return "{}".format(familias.get(pk=form.initial["familia"]))
        else:
            return "{}".format(familias.get(pk=form.cleaned_data["familia"].pk))
    except:
        return ""


@register.filter
def to_dict(defaultdict, key=None):
    return dict(defaultdict) if key is None else dict(defaultdict)[key]


@register.filter
def from_dict(dictionary, key):
    return dictionary[key]


@register.filter
def sum_dict(dictionary):
    return sum(dictionary.values())
