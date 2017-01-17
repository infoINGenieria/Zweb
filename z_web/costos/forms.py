from django import forms
from functools import partial, wraps
from django.forms.models import ModelForm, BaseInlineFormSet
from django.forms.formsets import BaseFormSet, formset_factory

from core.models import Obras
from parametros.models import Periodo, FamiliaEquipo


class PeriodoSelectForm(forms.Form):
    periodo = forms.ModelChoiceField(queryset=Periodo.objects.all())


class CopiaCostoForm(forms.Form):
    TIPO_COSTO = (
        ('costomanoobra', 'Costos Mano de Obra'),
        ('costosubcontrato', 'Costos Subcontratos'),
        ('lubricantefluidoshidro', 'Costos de Lubricantes y Fluidos Hidraulicos'),
        ('trenrodaje', 'Costos de Tren de Rodaje'),
        ('reservereparaciones', 'Reserva de reparaciones'),
        ('costoposesion', 'Costos de posesión'),
        ('materialestotal', 'Costos de Materiales'),
    )
    tipo_costos = forms.MultipleChoiceField(choices=TIPO_COSTO, widget=forms.CheckboxSelectMultiple())
    de_periodo = forms.ModelChoiceField(queryset=Periodo.objects.all(), label="Periodo origen")
    a_periodo = forms.ModelChoiceField(queryset=Periodo.objects.all(), label="Periodo destino")
    recalcular = forms.BooleanField(required=False, initial=False, label="¿Recalcular costos?",
                                    help_text="Al seleccionar esta opción, el valor de cada costos será recalculado "
                                              "según el valor del dolar para el periodo destino")


class CostoItemForm(forms.Form):
    monto = forms.FloatField(required=False)
    obra = forms.ModelChoiceField(Obras.objects.filter(es_cc=True), widget=forms.HiddenInput())


class CostoItemFamiliaForm(forms.Form):
    monto_hora = forms.FloatField(required=False)
    monto_mes = forms.FloatField(required=False)
    familia = forms.ModelChoiceField(FamiliaEquipo.objects.all(), widget=forms.HiddenInput())

