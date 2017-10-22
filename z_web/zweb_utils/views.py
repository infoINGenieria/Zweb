from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login, logout as django_logout
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.core.urlresolvers import reverse
from django.utils import six
from django.utils.encoding import force_text

# https://github.com/django/django/blob/master/django/contrib/auth/mixins.py


class AccessMixin(object):
    """
    Abstract CBV mixin that gives access mixins the same customizable
    functionality.
    """
    login_url = None
    permission_denied_message = ''
    raise_exception = False
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_login_url(self):
        """
        Override this method to override the login_url attribute.
        """
        login_url = self.login_url or settings.LOGIN_URL
        if not login_url:
            raise ImproperlyConfigured(
                '{0} is missing the login_url attribute. Define {0}.login_url, settings.LOGIN_URL, or override '
                '{0}.get_login_url().'.format(self.__class__.__name__)
            )
        return force_text(login_url)

    def get_permission_denied_message(self):
        """
        Override this method to override the permission_denied_message attribute.
        """
        return self.permission_denied_message

    def get_redirect_field_name(self):
        """
        Override this method to override the redirect_field_name attribute.
        """
        return self.redirect_field_name

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())


class LoginRequiredMixin(AccessMixin):
    """
    CBV mixin which verifies that the current user is authenticated.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return self.handle_no_permission()
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class PermissionRequiredMixin(AccessMixin):
    """
    CBV mixin which verifies that the current user has all specified
    permissions.
    """
    permission_required = None

    def get_permission_required(self):
        """
        Override this method to override the permission_required attribute.
        Must return an iterable.
        """
        if self.permission_required is None:
            raise ImproperlyConfigured(
                '{0} is missing the permission_required attribute. Define {0}.permission_required, or override '
                '{0}.get_permission_required().'.format(self.__class__.__name__)
            )
        if isinstance(self.permission_required, six.string_types):
            perms = (self.permission_required, )
        else:
            perms = self.permission_required
        return perms

    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return self.handle_no_permission()
        return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)


class LoginAndPermissionRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    pass


def logout(request):
    cache.delete("user_menu_{}".format(request.user.pk))
    messages.add_message(request, messages.SUCCESS, u"Has cerrado la sesión exitosamente.")
    return django_logout(request, next_page=reverse('login'))


def generate_menu_user(user):
    menu = []
    if user.has_perm('costos.can_view_panel_control'):
        ext = user.extension
        if not ext.unidad_negocio or (ext.unidad_negocio and ext.unidad_negocio.codigo == 'MS'):
            menu.append({
                'name': "Panel de control", 'icon': 'dashboard',
                'url': reverse('frontend:ms_panel_control'), 'section': "{}".format(ext.unidad_negocio or 'Movimiento de suelo'),
                'btn_class': 'success'
            })
        if not ext.unidad_negocio or (ext.unidad_negocio and ext.unidad_negocio.codigo == 'OS'):
            menu.append({
                'name': "Tablero de control", 'icon': 'area-chart',
                'url': '/~/tablero-control/os/', 'section': "{}".format(ext.unidad_negocio or 'Obras de superficie'),
                'btn_class': 'default'
            })
    if user.has_perm('costos.can_manage_costos'):
        menu.append({'name': "Costos", 'icon': 'list',
                     'url': reverse('costos:index'), 'section': 'Administrar costos y avance de obra', 'btn_class': 'primary'})
    if user.has_perm("costos.can_generate_reports"):
        menu.append({'name': "Reportes", 'icon': 'print',
                     'url': reverse('reportes:index'), 'section': 'Generar y visualizar reportes', 'btn_class': 'warning'})
    if user.has_perm("organizacion.can_manage_presupuestos"):
        menu.append({'name': "Presupuestos", 'icon': 'file-text-o',
                     'url': '/~/presupuestos/', 'section': 'Administrar presupuestos', 'btn_class': 'info'})
    if user.has_perm("registro_can_manage_certificaciones"):
        menu.append({'name': "Certificaciones", 'icon': 'certificate',
                     'url': '/~/certificaciones/index', 'section': 'Administrar certificaciones', 'btn_class': 'success'})
    if user.is_staff:
        menu.append({'name': "Administración", 'icon': 'cogs',
                     'url': reverse('admin:index'), 'section': 'Gestionar entidades',
                     'btn_class': 'default'})
    return menu
