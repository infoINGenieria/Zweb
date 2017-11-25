from django.forms import fields, widgets


class FlexibleDecimalField(fields.DecimalField):
    """
    Uso este field para decimales que aceptan . (dot) y , (comma) como separador decimal.
    """
    widget = widgets.TextInput

    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", ".")
        return super(FlexibleDecimalField, self).process_formdata(valuelist)

    def to_python(self, value):
        value = value.replace(",", ".")
        return super(FlexibleDecimalField, self).to_python(value)
