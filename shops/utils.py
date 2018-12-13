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