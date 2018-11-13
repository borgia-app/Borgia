from django.test import TestCase

from settings_data.models import Setting

def create_settings(values, settings_list):
    """
    Helper for creating settings in a list.
    """
    for index, tuple_value in enumerate(values):
        settings_list.append(Setting.objects.create(
            name=tuple_value[1] + str(index) + ' name',
            description=tuple_value[1] + str(index) + ' description',
            value=tuple_value[0],
            value_type=tuple_value[1]
        ))

class SettingTestCase(TestCase):
    """
    Tests for the Setting model.
    """
    def setUp(self):
        integer_values = [
            ('1', 'i'), ('1.0', 'i'), ('1.23', 'i'), 
            (1, 'i'), (1.0, 'i'), (1.1, 'i')
        ]
        float_values = [
            ('1.23', 'f'), ('1.0', 'f'), ('1', 'f'), (1.23, 'f'), (1, 'f')
        ]
        string_values = [
            ('hello', 's'), ('1', 's'), (1, 's')
        ]
        boolean_values = [
            ('True', 'b'), ('true', 'b'), (True, 'b'),
            ('False', 'b'), ('false', 'b'), (False, 'b'),
            (1, 'b'), (0, 'b')
            
        ]

        self.integer_settings = []
        self.float_settings = []
        self.string_settings = []
        self.boolean_settings = []

        create_settings(integer_values, self.integer_settings)
        create_settings(float_values, self.float_settings)
        create_settings(string_values, self.string_settings)
        create_settings(boolean_values, self.boolean_settings)

    def test_str(self):
        self.assertEqual(self.integer_settings[0].__str__(), 'i0 name')
        self.assertEqual(self.float_settings[0].__str__(), 'f0 name')
        self.assertEqual(self.string_settings[0].__str__(), 's0 name')
        self.assertEqual(self.boolean_settings[0].__str__(), 'b0 name')

    def test_get_value_integer(self):
        self.assertEqual(self.integer_settings[0].get_value(), 1)
        self.assertEqual(self.integer_settings[1].get_value(), 0)
        self.assertEqual(self.integer_settings[2].get_value(), 0)
        self.assertEqual(self.integer_settings[3].get_value(), 1)
        self.assertEqual(self.integer_settings[4].get_value(), 1)
        self.assertEqual(self.integer_settings[5].get_value(), 1)

    def test_get_value_float(self):
        self.assertEqual(self.float_settings[0].get_value(), 1.23)
        self.assertEqual(self.float_settings[1].get_value(), 1)
        self.assertEqual(self.float_settings[2].get_value(), 1)
        self.assertEqual(self.float_settings[3].get_value(), 1.23)
        self.assertEqual(self.float_settings[4].get_value(), 1)

    def test_get_value_string(self):
        self.assertEqual(self.string_settings[0].get_value(), 'hello')
        self.assertEqual(self.string_settings[1].get_value(), '1')
        self.assertEqual(self.string_settings[2].get_value(), '1')

    def test_get_value_boolean(self):
        self.assertEqual(self.boolean_settings[0].get_value(), True)
        self.assertEqual(self.boolean_settings[1].get_value(), True)
        self.assertEqual(self.boolean_settings[2].get_value(), True)
        self.assertEqual(self.boolean_settings[3].get_value(), False)
        self.assertEqual(self.boolean_settings[4].get_value(), False)
        self.assertEqual(self.boolean_settings[5].get_value(), False)
        self.assertEqual(self.boolean_settings[6].get_value(), True)
        self.assertEqual(self.boolean_settings[7].get_value(), False)

