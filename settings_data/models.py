from django.db import models


class Setting(models.Model):
    name = models.CharField('Nom', max_length=100)
    description = models.TextField('Description')
    value = models.CharField('Valeur', max_length=500)
    value_type = models.CharField('Type', max_length=1, choices=(('s', 'string'), ('i', 'integer'), ('f', 'float'),
                                                                 ('b', 'boolean')))

    def get_value(self):
        types = {
            's': str,
            'i': int,
            'f': float,
            'b': (lambda v: v.lower().startswith('t') or v.startswith('1'))
        }
        return types[self.value_type](self.value)