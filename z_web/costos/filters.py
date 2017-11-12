import django_filters

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from crispy_forms.bootstrap import StrictButton

from zweb_utils.tables_filters import CrispyFilters
from .models import Costo, CostoTipo, AvanceObra


class CostosFilter(CrispyFilters):

    class CostosFilterFormHelper(FormHelper):
        form_class = 'form-inline'
        form_method = 'get'
        layout = Layout(
            Div('tipo_costo', css_class="col-xs-6"),
            Div('relacionado_con', css_class="col-xs-6"),
            Div('periodo', css_class='col-xs-6'),
            Div('familia_equipo', css_class='col-xs-6'),
            Div('centro_costo', css_class="col-xs-12"),
            Div(
                StrictButton('Filtrar', type="submit", css_class='btn btn-primary'),
                css_class="col-xs-12")
        )

    helper = CostosFilterFormHelper
    tipo_costo = django_filters.ModelChoiceFilter(
        label='Tipo de costo', queryset=CostoTipo.objects.all())
    relacionado_con = django_filters.ChoiceFilter(
        label='Relacionado con', choices=CostoTipo.RELACIONADO_CON,
        name='tipo_costo__relacionado_con')

    class Meta:
        model = Costo
        fields = ('tipo_costo', 'relacionado_con', 'periodo',
                  'centro_costo', 'familia_equipo', )


class AvanceObraFilter(CrispyFilters):
    class AvanceObraFilterFormHelper(FormHelper):
        form_class = 'form-inline'
        form_method = 'get'
        layout = Layout(
            Div('periodo', css_class="col-xs-6"),
            Div('centro_costo', css_class="col-xs-12"),
            Div(
                StrictButton('Filtrar', type="submit", css_class='btn btn-primary'),
                css_class="col-xs-6")
        )

    helper = AvanceObraFilterFormHelper

    class Meta:
        model = AvanceObra
        fields = ('periodo', 'centro_costo', )
