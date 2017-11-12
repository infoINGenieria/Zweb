# coding=utf-8
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin


class TableFilterListView(SingleTableMixin, FilterView):
    """
    Una vista que requiere autenticación, y espera que se defina la tabla y
    el filtrado de la misma
    """
    template_name = 'frontend/base_list.html'

    add_to_context = {}

    def get_context_data(self, **kwargs):
        ctx = super(TableFilterListView, self).get_context_data(**kwargs)
        ctx.update(self.add_to_context)
        return ctx


class ModalViewMixin(object):
    """
    Utilizar este mixin en las vistas que serán utilizadas con bootstrap modal.
    Exige definir un url_post_form para insertar en el template de manera de
    que el form cuente con un action válido.
    """
    template_name = "modal_base.html"

    url_post_form = None
    modal_title = ""

    def get_url_post_form(self):
        if self.url_post_form is not None:
            return self.url_post_form
        raise NotImplementedError("Debes definir este método en la subclase")

    def get_context_data(self, *args, **kwargs):
        ctx = super(ModalViewMixin, self).get_context_data(*args, **kwargs)
        ctx["url_post_form"] = self.get_url_post_form()
        ctx["modal_title"] = self.modal_title
        return ctx
