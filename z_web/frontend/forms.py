from django import forms

from core.models import Obras
from parametros.models import Periodo


class CustomPanelControlForm(forms.Form):
    periodo_ini = forms.ModelChoiceField(queryset=Periodo.objects.all(), label='Periodo inicial', required=True)
    periodo_fin = forms.ModelChoiceField(queryset=Periodo.objects.all(), label='Periodo final', required=False)
    centro_costos = forms.ModelMultipleChoiceField(
        queryset=Obras.get_centro_costos_ms(), label='Centro de costos', required=False,
        help_text="No seleccione ningún centro de costos para ver todos los involucrados en el rango de "
                  "periodos seleccionados")

    def clean(self):
        cleaned_data = super(CustomPanelControlForm, self).clean()
        if cleaned_data["periodo_fin"] and cleaned_data["periodo_ini"].fecha_fin > cleaned_data["periodo_fin"].fecha_inicio:
            self.add_error("periodo_ini", "El periodo inicial debe ser anterior al periodo final")
