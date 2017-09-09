from django import forms

from core.models import CCT


class OperarioHorasReporteForm(forms.Form):
    fecha_inicio = forms.DateField(widget=forms.TextInput(attrs={'class':'datepicker'}))
    fecha_fin = forms.DateField(widget=forms.TextInput(attrs={'class':'datepicker'}))
    cct = forms.ModelChoiceField(queryset=CCT.objects.all())


