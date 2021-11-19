from unittest import TestCase

from misipwgen.cumulative import CumulativeDistribution


class CumulativeDistributionTestCase(TestCase):
    def test_build(self):
        c = CumulativeDistribution(weights=[10, 20, 15])
        self.assertEqual(c.cumulative, {0: 10, 1: 30, 2: 45})

    def test_invert(self):
        c = CumulativeDistribution(weights=[10, 20, 15])

        for weight, expected_index in [
            (0, 0),
            (10, 0),
            (11, 1),
            (30, 1),
            (31, 2),
            (45, 2),
            (46, 2),
        ]:
            with self.subTest(weight=weight):
                self.assertEqual(c.invert(weight), expected_index)

    def test_weight_at(self):
        c = CumulativeDistribution(weights=[10, 20, 15])

        self.assertEqual(c.weight_at(0), 10)
        self.assertEqual(c.weight_at(1), 30)
        self.assertEqual(c.weight_at(2), 45)
