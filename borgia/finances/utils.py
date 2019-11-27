import decimal
import hashlib
import operator


def verify_token_lydia(params, token):
    """
    Verify request parameters according to Lydia's algorithm.

    If parameters are valid, the request is authenticated to be from Lydia and
    can be safely used.
    :note:: sig must be contained in the parameters dictionary.

    :warning:: token is private and must never be revealed.

    :param params: all parameters, including sig, mandatory.
    :type params: python dictionary
    :param token: token to be compared, mandatory.
    :type token: string

    :returns: True if parameters are valid, False else.
    :rtype: Boolean
    """
    try:
        sig = params['sig']
        del params['sig']
        h_sig_table = []
        sorted_params = sorted(params.items(), key=operator.itemgetter(0))
        for param in sorted_params:
            h_sig_table.append(param[0] + '=' + param[1])
        h_sig = '&'.join(h_sig_table)
        h_sig += '&' + token
        h_sig_hash = hashlib.md5(h_sig.encode())
        return h_sig_hash.hexdigest() == sig

    except KeyError:
        return False


def calculate_total_amount_lydia(recharging, base_fee, ratio_fee, tax_fee=1):
    """
    Calculate the total amount to pay through lydia
    """
    return decimal.Decimal(
        (recharging + tax_fee * base_fee)
        / (1 - tax_fee * ratio_fee / 100)
    ).quantize(decimal.Decimal('0.0001')).quantize(decimal.Decimal('.01'), decimal.ROUND_UP)
    # rounded to up. First round to 0.0001 is to remove float imprecision error, which lead 0.200000000001 to round to 0.21 instead of 0.20


def calculate_lydia_fee_from_total(total_amount, base_fee, ratio_fee, tax_fee=1):
    """
    Calculate the recharging amount through lydia
    """
    return decimal.Decimal(
        tax_fee * (base_fee + ratio_fee / 100 * total_amount)
    ).quantize(decimal.Decimal('0.0001')).quantize(decimal.Decimal('.01'), decimal.ROUND_UP)
    # rounded to up. First round to 0.0001 is to remove float imprecision error, which lead 0.200000000001 to round to 0.21 instead of 0.20
