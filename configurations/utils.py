from configurations.models import Configuration

"""
name: (String name, String description, String value_type, String value)
CENTER_NAME,
MARGIN_PROFIT,
LYDIA_MIN_PRICE, LYDIA_MAX_PRICE, LYDIA_API_TOKEN, LYDIA_VENDOR_TOKEN,
BALANCE_THRESHOLD_MAIL_ALERT, BALANCE_FREQUENCY_MAIL_ALERT,
BALANCE_THRESHOLD_PURCHASE
"""
CONFIGURATIONS_DEFAULT = {
    "CENTER_NAME": ("CENTER_NAME", "Nom du centre Borgia",
                    "s", "Center Name"),
    "MARGIN_PROFIT": ("MARGIN_PROFIT", "Marge (%) à appliquer sur le prix des produits calculés automatiquement",
                      "f", "5"),
    "LYDIA_MIN_PRICE": ("LYDIA_MIN_PRICE", "Valeur minimale (€) de rechargement en automatique par Lydia",
                        "f", "5"),
    "LYDIA_MAX_PRICE": ("LYDIA_MAX_PRICE", "Valeur maximale (€) de rechargement en automatique par Lydia",
                        "f", "500"),
    "LYDIA_API_TOKEN": ("LYDIA_API_TOKEN", "Clé API (privée)",
                        "s", "non définie"),
    "LYDIA_VENDOR_TOKEN": ("LYDIA_VENDOR_TOKEN", "Clé vendeur (publique)",
                           "s", "non définie"),
    "BALANCE_THRESHOLD_MAIL_ALERT": ("BALANCE_THRESHOLD_MAIL_ALERT", "Valeur seuil (€) en dessous de laquelle (strictement) l'alerte par email est activée",
                                     "f", "-10"),
    "BALANCE_FREQUENCY_MAIL_ALERT": ("BALANCE_FREQUENCY_MAIL_ALERT", "Fréquence (jours) à laquelle l'alerte mail est envoyée si le solde est inférieur à la valeur seuil",
                                     "i", "7"),
    "BALANCE_THRESHOLD_PURCHASE": ("BALANCE_THRESHOLD_PURCHASE", "Valeur seuil (€) en dessous de laquelle (strictement) la commande est impossible",
                                   "f", "0")
}


def configurations_safe_get(name):
    """
    Get the setting object regarding the name.
    If it doesn't exists, create one with default value in settings.py.

    :warning: This function raises errors if the name doens't correspond to
    something knew in settings.py, this error should not be excepted and should
    stop Borgia. These settings are crucial and an error means that settings.py
    isn't well configured.
    """
    default = CONFIGURATIONS_DEFAULT[name]
    setting, created = Configuration.objects.get_or_create(
        name=default[0],
        description=default[1],
        value_type=default[2]
    )
    if created:
        setting.value = default[3]
        setting.save()
    return setting