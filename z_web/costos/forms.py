from django import forms
from functools import partial, wraps
from django.forms.models import ModelForm, BaseInlineFormSet
from django.forms.formsets import BaseFormSet, formset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div

from core.models import Obras
from parametros.models import Periodo, FamiliaEquipo
from costos.models import Costo, CostoTipo, AvanceObra
from proyecciones.models import ProyeccionAvanceObra
from zweb_utils.fields import FlexibleDecimalField


# class PeriodoSelectForm(forms.Form):
    # periodo = forms.ModelChoiceField(queryset=Periodo.objects.all())


class CentroCostoSelectForm(forms.Form):
    centro_costo = forms.ModelChoiceField(queryset=Obras.objects.filter(es_cc=True))

    def __init__(self, user, *args, **kwargs):
        super(CentroCostoSelectForm, self).__init__(*args, **kwargs)
        self.fields["centro_costo"].queryset = Obras.get_centro_costos(user)

class CopiaCostoForm(forms.Form):
    tipo_costos = forms.ModelMultipleChoiceField(
        label="Tipos de costo", queryset=CostoTipo.objects.all(), widget=forms.CheckboxSelectMultiple())
    de_periodo = forms.ModelChoiceField(
        queryset=Periodo.con_parametros_costos.all(), label="Periodo de origen",
        help_text="Sólo se visualizan aquellos periodos con parámetros de costos asociados.")
    a_periodo = forms.ModelChoiceField(
        queryset=Periodo.con_parametros_costos.all(), label="Periodo de destino",
        help_text="Sólo se visualizan aquellos periodos con parámetros de costos asociados.")
    recalcular = forms.BooleanField(required=False, initial=False, label="¿Recalcular costos?",
                                    help_text="Al seleccionar esta opción, el valor de cada costos será recalculado "
                                              "según el valor del dolar para el periodo destino")


class CostoItemForm(forms.Form):
    monto = forms.FloatField(required=False)
    obra = forms.ModelChoiceField(Obras.objects.filter(es_cc=True), widget=forms.HiddenInput())


class CostoItemFamiliaForm(forms.Form):
    """
    :deprecated
    """
    monto_hora = forms.FloatField(required=False)
    monto_mes = forms.FloatField(required=False)
    familia = forms.ModelChoiceField(FamiliaEquipo.objects.all(), widget=forms.HiddenInput())


class PeriodoCCForm(forms.Form):
    periodo = forms.ModelChoiceField(
        queryset=Periodo.con_parametros_costos.all(),
        help_text="Sólo se visualizan aquellos periodos con parámetros de costos asociados.")
    centro_costo = forms.ModelChoiceField(
        label="Centro de costos", queryset=Obras.objects.filter(es_cc=True))

    def __init__(self, user, *args, **kwargs):
        super(PeriodoCCForm, self).__init__(*args, **kwargs)
        self.fields["centro_costo"].queryset = Obras.get_centro_costos(user)


class CostoCCForm(forms.Form):
    tipo_costo = forms.ModelChoiceField(CostoTipo.objects.filter(relacionado_con='cc'), widget=forms.HiddenInput())
    observacion = forms.CharField(label='Observación', required=False)
    monto_total = FlexibleDecimalField(label='Monto ($)', required=False)


class PeriodoCostoTipoForm(forms.Form):
    periodo = forms.ModelChoiceField(
        queryset=Periodo.con_parametros_costos.all(),
        help_text="Sólo se visualizan aquellos periodos con parámetros de costos asociados.")
    tipo_costo = forms.ModelChoiceField(
        CostoTipo.objects.filter(relacionado_con='eq'))


class CostoEquipoForm(forms.Form):
    monto_hora = FlexibleDecimalField(label='Monto ($/hs)', required=False)
    monto_mes = FlexibleDecimalField(label='Monto ($/mes)', required=False)
    monto_anio = FlexibleDecimalField(label='Monto ($/año)', required=False)
    observacion = forms.CharField(label='Observación', required=False)
    familia_equipo = forms.ModelChoiceField(FamiliaEquipo.objects.all(), widget=forms.HiddenInput())


class AvanceObraCreateForm(forms.ModelForm):
    periodo = forms.ModelChoiceField(queryset=Periodo.con_parametros_costos.all(), required=True)

    class Meta:
        model = AvanceObra
        fields = ('periodo', 'avance', 'observacion')

    def save(self, centro_costo, commit=True):
        avance = super(AvanceObraCreateForm, self).save(False)
        avance.centro_costo = centro_costo
        if commit:
            avance.save()
        return avance



"""
Forms usados por los popup
"""

class CostoEditPorCCForm(forms.ModelForm):
    periodo = forms.ModelChoiceField(queryset=Periodo.con_parametros_costos.all(), required=True)
    monto_total = FlexibleDecimalField()

    class Meta:
        model = Costo
        fields = ('periodo', 'centro_costo', 'monto_total', 'observacion', )

    def __init__(self, user, *args, **kwargs):
        super(CostoEditPorCCForm, self).__init__(*args, **kwargs)
        self.fields["centro_costo"].queryset = Obras.get_centro_costos(user)

        self.helper = FormHelper(self)
        self.helper.form_class = 'horizontal-form'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div('centro_costo', css_class='col-sm-12'),
            Div('periodo', css_class="col-sm-6"),
            Div('monto_total', css_class='col-sm-6'),
            Div('observacion', css_class="col-sm-12"),
        )


class CostoEditPorEquipoForm(forms.ModelForm):
    periodo = forms.ModelChoiceField(queryset=Periodo.con_parametros_costos.all(), required=True)
    monto_hora = FlexibleDecimalField(label='Monto ($/hs)', required=False)
    monto_mes = FlexibleDecimalField(label='Monto ($/mes)', required=False)
    monto_anio = FlexibleDecimalField(label='Monto ($/año)', required=False)

    class Meta:
        model = Costo
        fields = ('periodo', 'familia_equipo', 'monto_hora', 'monto_mes',
                  'monto_anio', 'observacion', )

    def __init__(self, user, *args, **kwargs):
        super(CostoEditPorEquipoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'horizontal-form'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('periodo', css_class="col-sm-6"),
                Div('familia_equipo', css_class='col-sm-6'),
                css_class="row"),
            Div(
                Div('monto_hora', css_class='col-sm-4'),
                Div('monto_mes', css_class='col-sm-4'),
                Div('monto_anio', css_class='col-sm-4'),
                Div('observacion', css_class="col-sm-12"),
                css_class='row'
            )
        )


class AvanceObraEditForm(forms.ModelForm):
    periodo = forms.ModelChoiceField(queryset=Periodo.con_parametros_costos.all(), required=True)
    avance = FlexibleDecimalField()

    class Meta:
        model = AvanceObra
        fields = ('periodo', 'centro_costo', 'avance', 'observacion', )

    def __init__(self, user, *args, **kwargs):
        super(AvanceObraEditForm, self).__init__(*args, **kwargs)
        self.fields["centro_costo"].queryset = Obras.get_centro_costos(user)
        self.helper = FormHelper(self)
        self.helper.form_class = 'horizontal-form'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div('centro_costo', css_class='col-sm-12'),
            Div('periodo', css_class="col-sm-6"),
            Div('avance', css_class='col-sm-6'),
            Div('observacion', css_class="col-sm-12"),
        )
