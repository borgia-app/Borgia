from django.test import TestCase

from configurations.models import Configuration

def create_configurations(values, configurations_list):
    """
    Helper for creating configurations in a list.
    """
    for index, tuple_value in enumerate(values):
        configurations_list.append(Configuration.objects.create(
            name=tuple_value[1] + str(index) + ' name',
            description=tuple_value[1] + str(index) + ' description',
            value=tuple_value[0],
            value_type=tuple_value[1]
        ))

class ConfigurationTestCase(TestCase):
    """
    Tests for the Configuration model.
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

        self.integer_configurations = []
        self.float_configurations = []
        self.string_configurations = []
        self.boolean_configurations = []

        create_configurations(integer_values, self.integer_configurations)
        create_configurations(float_values, self.float_configurations)
        create_configurations(string_values, self.string_configurations)
        create_configurations(boolean_values, self.boolean_configurations)

    def test_str(self):
        self.assertEqual(self.integer_configurations[0].__str__(), 'i0 name')
        self.assertEqual(self.float_configurations[0].__str__(), 'f0 name')
        self.assertEqual(self.string_configurations[0].__str__(), 's0 name')
        self.assertEqual(self.boolean_configurations[0].__str__(), 'b0 name')

    def test_get_value_integer(self):
        self.assertEqual(self.integer_configurations[0].get_value(), 1)
        self.assertEqual(self.integer_configurations[1].get_value(), 0)
        self.assertEqual(self.integer_configurations[2].get_value(), 0)
        self.assertEqual(self.integer_configurations[3].get_value(), 1)
        self.assertEqual(self.integer_configurations[4].get_value(), 1)
        self.assertEqual(self.integer_configurations[5].get_value(), 1)

    def test_get_value_float(self):
        self.assertEqual(self.float_configurations[0].get_value(), 1.23)
        self.assertEqual(self.float_configurations[1].get_value(), 1)
        self.assertEqual(self.float_configurations[2].get_value(), 1)
        self.assertEqual(self.float_configurations[3].get_value(), 1.23)
        self.assertEqual(self.float_configurations[4].get_value(), 1)

    def test_get_value_string(self):
        self.assertEqual(self.string_configurations[0].get_value(), 'hello')
        self.assertEqual(self.string_configurations[1].get_value(), '1')
        self.assertEqual(self.string_configurations[2].get_value(), '1')

    def test_get_value_boolean(self):
        self.assertEqual(self.boolean_configurations[0].get_value(), True)
        self.assertEqual(self.boolean_configurations[1].get_value(), True)
        self.assertEqual(self.boolean_configurations[2].get_value(), True)
        self.assertEqual(self.boolean_configurations[3].get_value(), False)
        self.assertEqual(self.boolean_configurations[4].get_value(), False)
        self.assertEqual(self.boolean_configurations[5].get_value(), False)
        self.assertEqual(self.boolean_configurations[6].get_value(), True)
        self.assertEqual(self.boolean_configurations[7].get_value(), False)
