import unittest
from django.test import TestCase

from django.core.exceptions import ObjectDoesNotExist

from users.models import User
from django.contrib.auth.models import Permission, Group
from borgia.utils import *


class LateralMenuModelTestCase(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='group_test')
        self.add_permission = Permission.objects.get(codename='add_user')
        self.list_permission = Permission.objects.get(codename='list_user')

    def test_none(self):
        self.assertEqual(
            lateral_menu_model(User, self.group, 1),
            None
        )

    def test_add(self):
        self.group.permissions.add(self.add_permission)
        self.assertEqual(
            lateral_menu_model(User, self.group, 1),
            {
                'label': 'User',
                'icon': 'database',
                'id': 1,
                'subs': [
                    {
                        'label': 'Nouveau',
                        'icon': 'plus',
                        'id': 11,
                        'url': '#'
                    }
                ]
            }
        )

    def test_list(self):
        self.group.permissions.add(self.list_permission)
        self.assertEqual(
            lateral_menu_model(User, self.group, 1),
            {
                'label': 'User',
                'icon': 'database',
                'id': 1,
                'subs': [
                    {
                        'label': 'Liste',
                        'icon': 'list',
                        'id': 11,
                        'url': '#'
                    }
                ]
            }
        )

    def test_add_list(self):
        self.group.permissions.add(self.add_permission)
        self.group.permissions.add(self.list_permission)
        self.assertEqual(
            lateral_menu_model(User, self.group, 1),
            {
                'label': 'User',
                'icon': 'database',
                'id': 1,
                'subs': [
                    {
                        'label': 'Nouveau',
                        'icon': 'plus',
                        'id': 11,
                        'url': '#'
                    },
                    {
                        'label': 'Liste',
                        'icon': 'list',
                        'id': 12,
                        'url': '#'
                    }
                ]
            }
        )


class LateralMenuTreasurerTestCase(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='Trésoriers')
        self.add_user_permission = Permission.objects.get(codename='add_user')
        self.list_user_permission = Permission.objects.get(codename='list_user')
        self.add_productbase_permission = Permission.objects.get(codename='add_productbase')
        self.list_productbase_permission = Permission.objects.get(codename='list_productbase')

    def test_none(self):
        self.assertEqual(
            lateral_menu_treasurer(),
            []
        )

    def test_regular(self):
        self.group.permissions.add(self.add_user_permission)
        self.group.permissions.add(self.list_user_permission)
        self.group.permissions.add(self.add_productbase_permission)
        self.group.permissions.add(self.list_productbase_permission)
        self.assertCountEqual(
            lateral_menu_treasurer(),
            []
        )
