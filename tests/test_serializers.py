from decimal import Decimal

from django.test import TestCase
from django.template import defaultfilters

from dynamic_preferences import serializers


class TestSerializers(TestCase):

    def test_boolean_serialization(self):
        s = serializers.BooleanSerializer

        self.assertEqual(s.serialize(True), "True")
        self.assertEqual(s.serialize(False), "False")
        with self.assertRaises(s.exception):
            s.serialize('yolo')

    def test_boolean_deserialization(self):

        s = serializers.BooleanSerializer

        for v in s.true:
            self.assertEqual(s.deserialize(v), True)

        for v in s.false:
            self.assertEqual(s.deserialize(v), False)

        with self.assertRaises(s.exception):
            s.deserialize("I'm a true value")

    def test_int_serialization(self):

        s = serializers.IntSerializer

        self.assertEqual(s.serialize(1), "1")
        self.assertEqual(s.serialize(666), "666")
        self.assertEqual(s.serialize(-144), "-144")
        self.assertEqual(s.serialize(0), "0")
        self.assertEqual(s.serialize(123456), "123456")

        with self.assertRaises(s.exception):
            s.serialize("I'm an integer")

    def test_decimal_serialization(self):

        s = serializers.DecimalSerializer

        self.assertEqual(s.serialize(Decimal("1")), "1")
        self.assertEqual(s.serialize(Decimal("-1")), "-1")
        self.assertEqual(s.serialize(Decimal("-666.6")), "-666.6")
        self.assertEqual(s.serialize(Decimal("666.6")), "666.6")

        with self.assertRaises(s.exception):
            s.serialize("I'm a decimal")

    def test_float_serialization(self):

        s = serializers.FloatSerializer

        self.assertEqual(s.serialize(1.0), "1.0")
        self.assertEqual(s.serialize(-1.0), "-1.0")
        self.assertEqual(s.serialize(-666.6), "-666.6")
        self.assertEqual(s.serialize(666.6), "666.6")

        with self.assertRaises(s.exception):
            s.serialize("I'm a float")

    def test_float_deserialization(self):

        s = serializers.FloatSerializer

        self.assertEqual(s.deserialize("1.0"), float("1.0"))
        self.assertEqual(s.deserialize("-1.0"), float("-1.0"))
        self.assertEqual(s.deserialize("-666.6"), float("-666.6"))
        self.assertEqual(s.deserialize("666.6"), float("666.6"))

        with self.assertRaises(s.exception):
            s.serialize("I'm a float")

    def test_int_deserialization(self):

        s = serializers.DecimalSerializer

        self.assertEqual(s.deserialize("1"), Decimal("1"))
        self.assertEqual(s.deserialize("-1"), Decimal("-1"))
        self.assertEqual(s.deserialize("-666.6"), Decimal("-666.6"))
        self.assertEqual(s.deserialize("666.6"), Decimal("666.6"))

        with self.assertRaises(s.exception):
            s.serialize("I'm a decimal!")

    def test_string_serialization(self):

        s = serializers.StringSerializer

        self.assertEqual(s.serialize("Bonjour"), "Bonjour")
        self.assertEqual(s.serialize("12"), "12")
        self.assertEqual(s.serialize(
            "I'm a long sentence, but I rock"), "I'm a long sentence, but I rock")

        # check for HTML escaping
        kwargs = {"escape_html": True, }
        self.assertEqual(
            s.serialize(
                "<span>Please, I don't wanna disappear</span>", **kwargs),
            defaultfilters.force_escape(
                "<span>Please, I don't wanna disappear</span>")
        )

        with self.assertRaises(s.exception):
            s.serialize(('I', 'Want', 'To', 'Be', 'A', 'String'))

    def test_string_deserialization(self):

        s = serializers.StringSerializer
        self.assertEqual(s.deserialize("Bonjour"), "Bonjour")
        self.assertEqual(s.deserialize("12"), "12")
        self.assertEqual(s.deserialize(
            "I'm a long sentence, but I rock"), "I'm a long sentence, but I rock")

        kwargs = {"escape_html": True, }
        self.assertEqual(
            s.deserialize(
                s.serialize("<span>Please, I don't wanna disappear</span>", **kwargs)),
            defaultfilters.force_escape(
                "<span>Please, I don't wanna disappear</span>")
        )
