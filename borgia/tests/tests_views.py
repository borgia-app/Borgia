from django.contrib.auth.models import Group, Permission
from django.test import Client, TestCase
from django.urls import reverse

from users.models import User


class BaseBorgiaViewsTestCase(TestCase):
    def setUp(self):
        members_group = Group.objects.create(name='gadzarts')
        presidents_group = Group.objects.create(name='presidents')
        presidents_group.permissions.set(Permission.objects.all())
        # Group specials NEED to be created (else raises errors) :
        specials_group = Group.objects.create(name='specials')
        specials_group.permissions.set([])
        specials_group.save()
        
        self.user1 = User.objects.create(username='user1', balance=53)
        self.user1.groups.add(members_group)
        self.user1.groups.add(presidents_group)
        self.user2 = User.objects.create(username='user2', balance=144)
        self.user2.groups.add(specials_group)
        self.user3 = User.objects.create(username='user3')
        self.client1 = Client()
        self.client1.force_login(self.user1)
        self.client2 = Client()
        self.client2.force_login(self.user2)
        self.client3 = Client()
        self.client3.force_login(self.user3)