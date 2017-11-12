import random
import string
import factory

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission, User

from parametros.models import Periodo
from .models import CostoParametro


def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.LazyAttribute(lambda t: random_string())
    email = factory.LazyAttribute(lambda t: "{}@test.com".format(random_string()))


class PeriodoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Periodo


class CostoParametroFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CostoParametro


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.useradmin = User.objects.create(
            username="superuser",
            email='superuser@test.com')
        self.useradmin.set_password('password')
        self.useradmin.is_staff = True
        self.useradmin.is_superuser = True
        self.useradmin.save()

        self.user = User.objects.create(username='user', email='user@test.com')
        self.user.set_password('secret')
        self.user.save()
        self.user.user_permissions.add(Permission.objects.get(codename='can_manage_costos'))

        self.client = Client()
        self.client.login(username='user', password='secret')

        self.user2 = User.objects.create(username='user2', email='user2@test.com')
        self.user2.set_password('secret')
        self.user2.save()


class FirstTest(BaseTestCase):

    def test_login_logout_and_index_redirection(self):
        self.client.logout()
        response = self.client.get(reverse('admin:index'))
        self.assertRedirects(response, '%s?next=/admin/' % reverse('admin:login'))

        response = self.client.post(
            reverse('admin:login'),
            {'username': 'superuser',
             'password': 'password'}
        )

        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('admin:logout'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('admin:index'))
        self.assertRedirects(response, '%s?next=/admin/' % reverse('admin:login'))

"""
- ver menu si tiene permisos
-test listado
- test listado filtros
- test edit
- test delete
- test table segun tipo costo
- copiar costos
- test cargar costos CC
- test cargar costos EQ

"""

class CostosViewsTests(BaseTestCase):
    def test_costos_index_no_perm(self):
        self.client.logout()
        self.client.login(username=self.user2.username, password='secret')
        response = self.client.get(reverse('costos:costos_list'))
        self.assertEqual(response.status_code, 403)

    def test_costos_index_success(self):
        response = self.client.get(reverse('costos:costos_list'))
        self.assertEqual(response.status_code, 200)


