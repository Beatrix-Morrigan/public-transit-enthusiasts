import sys
import unittest


sys.path.insert(0, "../")
from src.PatrolRoutes.Duration import BaseDuration, Minutes, Seconds


class Duration_BaseDuration_tests(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.m1 = Minutes(3)
		cls.m2 = Minutes(-3)
		
		cls.s1 = Seconds(180)
		
	def test_rounding_error_print(self):
		BaseDuration._round_error_printed = False

		with self.assertWarns(BaseDuration.DurationRoundingWarning):
			Minutes(3.01)

		_ = Minutes(3.01)

	def test_init_with_baseduration(self):
		new_s1 = Seconds(self.m1)
		new_m1 = Minutes(self.s1)

		self.assertEqual(new_s1, Seconds(180))
		self.assertEqual(new_m1, Minutes(3))

	def test_abs(self):
		self.assertEqual(
			abs(self.m2),
			self.m1
		)

	def test_add(self):
		res1 = Minutes(3) + Seconds(60)
		self.assertIsInstance(res1, Minutes)
		self.assertEqual(res1, Minutes(4))

		res2 = Seconds(60) + Minutes(3)
		self.assertIsInstance(res2, Seconds)
		self.assertEqual(res2, Minutes(4))
		self.assertEqual(res2, Seconds(240))

	def test_sub(self):
		res1 = Minutes(3) - Seconds(30)
		self.assertIsInstance(res1, Minutes)
		self.assertEqual(res1, Minutes(2.5))

	def test_eq(self):
		self.assertEqual(self.m1, Minutes(3))
		self.assertEqual(self.m1, self.s1)
		self.assertNotEqual(self.m1, self.m2)

		BaseDuration._round_error_printed = True
		m = Minutes(3.67)

		self.assertEqual(m.unit_value, 3 + (float(2)/float(3)))

	def test_repr(self):
		self.assertEqual(
			repr(self.m1),
			"Minutes(unit_value = 3, seconds = 180, scale = 60)"
		)

	def test_str(self):
		self.assertEqual(str(Minutes(1)), "1 minute")
		self.assertEqual(str(Minutes(2)), "2 minutes")
		self.assertEqual(f"time: {self.m1}", "time: 3 minutes")

	def test_ne(self):
		self.assertTrue(Minutes(1) != Minutes(2))
		self.assertFalse(Minutes(1) != Minutes(1))

	def test_le(self):
		self.assertTrue(Minutes(1) <= Minutes(2))
		self.assertTrue(Minutes(1) <= Minutes(1))
		self.assertFalse(Minutes(3) <= Minutes(2))

	def test_lt(self):
		self.assertLess(Minutes(1), Seconds(61))
		self.assertFalse(Minutes(2) < Minutes(1))
		self.assertFalse(Minutes(2) < Minutes(2))

	def test_ge(self):
		self.assertTrue(Seconds(61) >= Minutes(1))
		self.assertTrue(Seconds(61) >= Seconds(61))
		self.assertFalse(Minutes(1) >= Minutes(2))

	def test_gt(self):
		self.assertGreater(Seconds(61), Minutes(1))
		self.assertFalse(Minutes(1) > Minutes(2))
		self.assertFalse(Minutes(2) > Minutes(2))

	def test_mul_rmul(self):
		self.assertEqual(
			Seconds(60) * 3,
			Minutes(3)
		)
		self.assertEqual(
			3 * Seconds(60),
			Minutes(3)
		)

		BaseDuration._round_error_printed = True
		self.assertEqual(
			Seconds(60) * 1.001,
			Minutes(1)
		)

	def test_truediv_rtruediv_floordiv_rfloordiv(self):
		self.assertEqual(
			Seconds(60) / 3,
			Seconds(20)
		)

		BaseDuration._round_error_printed = True
		self.assertEqual(
			Seconds(60) / 3.001,
			Seconds(20)
		)

		self.assertEqual(
			Seconds(60) // 7,
			Seconds(8)
		)