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

@register.simple_tag
def get_cat_pb_field(form, category_pk, product_base_pk):
    """

    """
    return form['productbase_%s_category_%s' % (product_base_pk, category_pk)]
