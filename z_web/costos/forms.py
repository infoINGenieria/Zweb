from django import forms
from functools import partial, wraps
from django.forms.models import ModelForm, BaseInlineFormSet
from django.forms.formsets import BaseFormSet, formset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div

from core.models import Obras
from parametros.models import Periodo, FamiliaEquipo
from costos.models import CostoReal, CostoTipo, CostoProyeccion, AvanceObraReal, AvanceObraProyeccion, AvanceObra


class PeriodoSelectForm(forms.Form):
    periodo = forms.ModelChoiceField(queryset=Periodo.objects.all())


class CentroCostoSelectForm(forms.Form):
    centro_costo = forms.ModelChoiceField(queryset=Obras.objects.filter(es_cc=True))


class CopiaCostoForm(forms.Form):
    tipo_costos = forms.ModelMultipleChoiceField(
        label="Tipos de costo", queryset=CostoTipo.objects.all(), widget=forms.CheckboxSelectMultiple())
    de_periodo = forms.ModelChoiceField(queryset=Periodo.objects.all(), label="Periodo de origen")
    a_periodo = forms.ModelChoiceField(queryset=Periodo.objects.all(), label="Periodo de destino")
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
    periodo = forms.ModelChoiceField(queryset=Periodo.objects.all())
    centro_costo = forms.ModelChoiceField(
        label="Centro de costos", queryset=Obras.objects.filter(es_cc=True))


class CostoCCForm(forms.Form):
    tipo_costo = forms.ModelChoiceField(CostoTipo.objects.filter(relacionado_con='cc'), widget=forms.HiddenInput())
    observacion = forms.CharField(label='Observación', required=False)
    monto_total = forms.DecimalField(label='Monto ($)', required=False)


class PeriodoCostoTipoForm(forms.Form):
    periodo = forms.ModelChoiceField(queryset=Periodo.objects.all())
    tipo_costo = forms.ModelChoiceField(
        CostoTipo.objects.filter(relacionado_con='eq'))


class CostoEquipoForm(forms.Form):
    monto_hora = forms.DecimalField(label='Monto ($/hs)', required=False)
    monto_mes = forms.DecimalField(label='Monto ($/mes)', required=False)
    monto_anio = forms.DecimalField(label='Monto ($/año)', required=False)
    observacion = forms.CharField(label='Observación', required=False)
    familia_equipo = forms.ModelChoiceField(FamiliaEquipo.objects.all(), widget=forms.HiddenInput())


class AvanceObraCreateForm(forms.ModelForm):
    periodo = forms.ModelChoiceField(queryset=Periodo.objects.all(), required=True)

    class Meta:
        model = AvanceObra
        fields = ('periodo', 'avance', 'observacion')

    def save(self, centro_costo, es_proyeccion, commit=True):
        avance = super(AvanceObraCreateForm, self).save(False)
        avance.centro_costo = centro_costo
        avance.es_proyeccion = es_proyeccion
        if commit:
            avance.save()
        return avance



"""
Forms usados por los popup
"""

class CostoEditPorCCForm(forms.ModelForm):

    class Meta:
        model = CostoReal
        fields = ('periodo', 'centro_costo', 'monto_total', 'observacion', )

    def __init__(self, *args, **kwargs):
        super(CostoEditPorCCForm, self).__init__(*args, **kwargs)
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

    class Meta:
        model = CostoReal
        fields = ('periodo', 'familia_equipo', 'monto_hora', 'monto_mes',
                  'monto_anio', 'observacion', )

    def __init__(self, *args, **kwargs):
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


class ProyeccionEditPorCCForm(CostoEditPorCCForm):

    class Meta:
        model = CostoProyeccion
        fields = ('periodo', 'centro_costo', 'monto_total', 'observacion', )


class ProyeccionEditPorEquipoForm(CostoEditPorEquipoForm):

    class Meta:
        model = CostoProyeccion
        fields = ('periodo', 'familia_equipo', 'monto_hora', 'monto_mes',
                  'monto_anio', 'observacion', )


class AvanceObraEditForm(forms.ModelForm):

    class Meta:
        model = AvanceObraReal
        fields = ('periodo', 'centro_costo', 'avance', 'observacion', )

    def __init__(self, *args, **kwargs):
        super(AvanceObraEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'horizontal-form'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div('centro_costo', css_class='col-sm-12'),
            Div('periodo', css_class="col-sm-6"),
            Div('avance', css_class='col-sm-6'),
            Div('observacion', css_class="col-sm-12"),
        )


class AvanceObraProyectadoEditForm(AvanceObraEditForm):

    class Meta:
        model = AvanceObraProyeccion
        fields = ('periodo', 'centro_costo', 'avance', 'observacion')
