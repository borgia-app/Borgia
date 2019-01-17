from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from shops.models import Shop


class CreateShopGroupTestCase(TestCase):
    def setUp(self):
        self.shop1 = Shop.objects.create(
            name="shop1",
            description="The first shop ever.",
            color="#F4FA58")

    def test_groups_creation(self):
        "Test creation of shop management groups"
        try:
            Group.objects.get(name='chiefs-'+self.shop1.name)
            Group.objects.get(name='associates-'+self.shop1.name)
        except ObjectDoesNotExist:
            self.fail("Shop creation should also create management groups")
