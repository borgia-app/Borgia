from django.db import models


class Configuration(models.Model):
    """
    Define a configuration parameter.

    Such configurations are set in option in the Borgia UI but administrators. They
    define how the application behave and which modules are enable. For Shop
    modules, please refer to attributes in the Shop model.

    :param name: name of the parameter, mandatory. Should be in capital letter
    to show that it's a constant in the application. Must be unique.
    :param description: description on the parameter, mandatory. One should
    indicate the unit of the parameter value here.
    :param value: value, mandatory.
    :param value_type: type of the value, mandatory.
    :type name: string
    :type description: string
    :type value: string
    :type value_type: string, must be in TYPE_CHOICES

    :warning:: value must be a string. However it can be a string integer/float
    of course, example: '1.10'. The output value of this parameter is going
    to be in the right type, please refer to get_value method.
    :note:: It's possible to use directly some value typed (boolean, integer,
    float) not in string. Refer to tests (tests_models.py) for further
    information and cases. One can use the following :
    +-----------+---------+--------+---------+
    | Integer   | Float   | String | Boolean |
    +===========+=========+========+=========+
    | x         | x.y     | x      | True    |
    +-----------+---------+--------+---------+
    | 'x'       | 'x.y'   |        | 'True'  |
    +-----------+---------+--------+---------+
    |           | x       |        | 'true'  |
    +-----------+---------+--------+---------+
    |           | 'x'     |        |         |
    +-----------+---------+--------+---------+
    where:
    - 'x' : string,
    - x : integer,
    - x.y : float
    - True is a boolean (same for False of course)

    All other cases are going to raise exceptions.
    """
    TYPE_CHOICES = (
        ('s', 'string'), ('i', 'integer'), ('f', 'float'), ('b', 'boolean'))

    name = models.CharField('Nom', max_length=100, unique=True)
    description = models.TextField('Description')
    value = models.CharField('Valeur', max_length=500)
    value_type = models.CharField('Type', max_length=1, choices=TYPE_CHOICES)

    class Meta:
        """
        :note:: Initial Django Permission (change, view) are added.
        """
        default_permissions = ('change', 'view',)

    def __str__(self):
        """
        Return the display name of Configuration object.

        :returns: name
        :rtype: string
        """
        return self.name

    def get_value(self):
        """
        Return the value of the parameter with the right type.

        :returns: value with the type defined in attribute value_type
        :rtype: type defined in the attribute value_type
        :raises: ValueError when integer is defined with a float.
        :raises: AttributeError when boolean not well defined.

        :note:: Every type seems (refer to tests) to be handle by the 'else',
        but not direct boolean.
        """
        types = {
            's': str,
            'i': int,
            'f': float,
            'b': bool
        }
        try:
            rtype = types[self.value_type]
            if rtype == bool:
                return self.value in ["True", "true", True, 1]
            else:
                return rtype(self.value)
        except ValueError:
            if rtype == int:
                return 0
            elif rtype == float:
                return 0.0
            elif rtype == bool:
                return False
            else:
                return ""
