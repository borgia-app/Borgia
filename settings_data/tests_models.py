from django.test import TestCase

from settings_data.models import Setting


class SettingTestCase(TestCase):
    def setUp(self):
        test_array = [
            ('1', 'i'), ('1.0', 'i'), ('1.23', 'i'), (1, 'i'), (1.0, 'i'),
            (1.1, 'i'),
            ('1.23', 'f'), ('1.0', 'f'), ('1', 'f'), (1.23, 'f'), (1, 'f'),
            ('hello', 's'), ('1', 's'), (1, 's'),
            ('True', 'b'), ('False', 'b'), (True, 'b'), (False, 'b'), (1, 'b'),
            ('true', 'b'), ('false', 'b')
        ]
        self.s = []
        for i, t in enumerate(test_array):
            self.s.append(Setting.objects.create(
                name='s'+str(i)+' name',
                description='s'+str(i)+' description',
                value=t[0],
                value_type=t[1]
            )
            )

    def test_str(self):
        self.assertEqual(
            self.s[0].__str__(),
            's0 name'
        )

    def test_get_value_integer(self):
        self.assertEqual(
            self.s[0].get_value(),
            1
        )
        self.assertRaises(
            ValueError,
            self.s[1].get_value,
        )
        self.assertRaises(
            ValueError,
            self.s[2].get_value,
        )
        self.assertEqual(
            self.s[3].get_value(),
            1
        )
        self.assertRaises(
            ValueError,
            self.s[4].get_value,
        )
        self.assertRaises(
            ValueError,
            self.s[5].get_value,
        )

    def test_get_value_float(self):
        self.assertEqual(
            self.s[6].get_value(),
            1.23
        )
        self.assertEqual(
            self.s[7].get_value(),
            1
        )
        self.assertEqual(
            self.s[8].get_value(),
            1
        )
        self.assertEqual(
            self.s[9].get_value(),
            1.23
        )
        self.assertEqual(
            self.s[10].get_value(),
            1
        )

    def test_get_value_string(self):
        self.assertEqual(
            self.s[11].get_value(),
            'hello'
        )
        self.assertEqual(
            self.s[12].get_value(),
            '1'
        )
        self.assertEqual(
            self.s[13].get_value(),
            '1'
        )

    def test_get_value_boolean(self):
        self.assertEqual(
            self.s[14].get_value(),
            True
        )
        self.assertEqual(
            self.s[15].get_value(),
            False
        )
        self.assertEqual(
            self.s[16].get_value(),
            True
        )
        self.assertEqual(
            self.s[17].get_value(),
            False
        )
        self.assertRaises(
            AttributeError,
            self.s[18].get_value
        )
        self.assertEqual(
            self.s[19].get_value(),
            True
        )
        self.assertEqual(
            self.s[20].get_value(),
            False
        )
