import django_filters

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from crispy_forms.bootstrap import StrictButton

from zweb_utils.tables_filters import CrispyFilters
from .models import Costo, CostoTipo


class CostosFilter(CrispyFilters):

    class CostosFilterFormHelper(FormHelper):
        form_class = 'form-inline'
        form_method = 'get'
        layout = Layout(
            Div('tipo_costo', css_class="col-xs-12"),
            Div('periodo', css_class='col-xs-6'),
            Div('familia_equipo', css_class='col-xs-6'),
            Div('centro_costo', css_class="col-xs-12"),
            Div(
                StrictButton('Filtrar', type="submit", css_class='btn btn-primary'),
                css_class="col-xs-12")
        )

    helper = CostosFilterFormHelper
    # tipo_costo = django_filters.DateFilter(
    #     label='Desde el', name='dia', lookup_expr='gte', widget=FechaWidget)
    # dia_end = django_filters.DateFilter(
    #     label='Hasta el', name='dia', lookup_expr='lte', widget=FechaWidget)
    tipo_costo = django_filters.ModelChoiceFilter(
        label='Tipo de costo', queryset=CostoTipo.objects.all(), required=True)
    # no_asistio = django_filters.BooleanFilter(label='¿Faltó?', name='no_asistio')
    # no_aviso = django_filters.BooleanFilter(label='¿Faltó y no avisó?', name='no_aviso')

    class Meta:
        model = Costo
        fields = ('tipo_costo', 'periodo', 'centro_costo', 'familia_equipo', )
