import random
import string
import factory

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
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

        self.client = Client()


class FirstTest(BaseTestCase):

    def test_login_logout_and_index_redirection(self):

        response = self.client.get(reverse('admin:index'))
        self.assertRedirects(response, '%s?next=/' % reverse('admin:login'))

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
        self.assertRedirects(response, '%s?next=/' % reverse('admin:login'))

