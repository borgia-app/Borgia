from django import template

register = template.Library()

@register.filter
def addstr(arg1, arg2):
    """
    Concatenate arg1 & arg2.

    :param arg1: first string, mandatory.
    :param arg2: second string, mandatory.
    :type arg1: string
    :type arg2: string
    :returns: arg1 and arg2 concatenated
    :rtype: string
    """
    return str(arg1) + str(arg2)

@register.filter
def get(dictionnary, key):
    """
    Return the value of the key in the dictionnary.

    This method can be used for instance for complex key which cannot be
    obtained by dict.key

    :param dictionnary: dictionnary, mandatory.
    :param key: key of the value, mandatory.
    :type dict: python dictionnary
    :type key: string
    """
    return dictionnary[key]
