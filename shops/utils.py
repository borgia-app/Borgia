from django.urls import reverse

from borgia.utils import simple_lateral_link
from shops.models import Shop

DEFAULT_PERMISSIONS_CHIEFS = ['add_user', 'view_user', 'add_recharging',
                              'change_shop', 'view_shop',
                              'add_product', 'change_product', 'delete_product', 'view_product',
                              'change_price_product',
                              'view_sale', 'use_operatorsalemodule',
                              'add_stockentry', 'view_stockentry',
                              'add_inventory', 'view_inventory']
DEFAULT_PERMISSIONS_ASSOCIATES = ['add_user', 'view_user',
                                  'view_shop',
                                  'add_product', 'change_product', 'view_product',
                                  'view_sale', 'use_operatorsalemodule',
                                  'add_stockentry', 'view_stockentry',
                                  'add_inventory', 'view_inventory']

def is_shop_manager(shop, user):
    if user in shop.get_managers():
        return True
    else:
        return False

def get_shops_managed(user):
    shop_list = []
    for shop in Shop.objects.all():
        if is_shop_manager(shop, user):
            shop_list.append(shop)
    
    return shop_list

def get_shops_tree(user, is_association_manager):
    shop_tree = []
    if is_association_manager:
        shop_managed = Shop.objects.all().exclude(pk=1)
    else:
        shop_managed = get_shops_managed(user)
        if len(shop_managed) == 0:
            return []

    for shop in shop_managed:
        shop_tree.append(
            simple_lateral_link(
                shop.name + ' Management',
                'briefcase',
                'lm_workboard',
                reverse('url_shop_workboard',
                        kwargs={'shop_pk': shop.pk})
            )
        )
    return shop_tree
