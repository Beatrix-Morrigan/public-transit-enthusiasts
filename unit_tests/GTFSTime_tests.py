import sys
import unittest


sys.path.insert(0, "../")
from src.PatrolRoutes.Duration import Seconds
from src.PatrolRoutes.GTFSTime import GTFSTime as GT



class GTFSTime_tests(unittest.TestCase):
	"""
	"""
	def test_init(self):
		self.assertEqual(
			GT("01:04:00"),
			3600 + (60 * 4)
		)

		self.assertEqual(
			GT("25:04:00"),
			(3600 * 25) + (60 * 4)
		)
		
		with self.assertRaises(GT.InvalidGTFSTimeException):
			GT("04")

		with self.assertRaises(GT.InvalidGTFSTimeException):
			GT("04:01:00:04")

	def test_add(self):
		self.assertEqual(
			GT("01:04:00") + Seconds(60*4),
			3600 + (60 * 8)
		)

	def test_subtract(self):
		self.assertEqual(
			GT("01:04:00") - Seconds(120),
			GT(3600 + (60*2))
		)

	def test_multiply(self):
		with self.assertRaises(RuntimeError):
			t = GT("01:00:00") * 2 #type: ignore

	def test_floordiv(self):
		with self.assertRaises(RuntimeError):
			t = GT("02:00:00") // 2 #type: ignore

	def test_rfloordiv(self):
		with self.assertRaises(RuntimeError):
			t = 2 // GT("02:00:00") #type: ignore

	def test_truediv(self):
		with self.assertRaises(RuntimeError):
			t = GT("02:00:00") / 2 #type: ignore

	def test_rtruediv(self):
		with self.assertRaises(RuntimeError):
			t = 2 / GT("02:00:00") #type: ignore

	def test_comp(self):
		self.assertGreater(
			GT("04:00:00"),
			GT("03:30:00")
		)

	def test_str(self):
		self.assertEqual(
			str(GT("01:30:00")),
			str("01:30:00")
		)

	def test_repr(self):
		self.assertEqual(
			repr(GT("01:30:00")),
			f'GTFSTime({3600+1800}|"01:30:00")'
		)

	def test_to_fstr(self):
		self.assertEqual(
			GT("10:00:00").to_fstr(),
			"10:00:00"
		)

		self.assertEqual(
			GT("11:02:30").to_fstr(short = True),
			"11:02"
		)

		self.assertEqual(
			GT("11:00:00").to_fstr(use_ampm=True),
			"11:00:00 AM"
		)

		self.assertEqual(
			GT("12:00:00").to_fstr(use_ampm=True),
			"12:00:00 PM"
		)

		self.assertEqual(
			GT("01:00:00").to_fstr(use_ampm=True),
			"01:00:00 AM"
		)

		self.assertEqual(
			GT("13:00:00").to_fstr(use_ampm=True),
			"01:00:00 PM"
		)

		self.assertEqual(
			GT("25:00:00").to_fstr(use_ampm=True),
			"01:00:00 AM-X"
		)

		self.assertEqual(
			GT("37:00:00").to_fstr(),
			"37:00:00"
		)

		with self.assertRaises(GT.InvalidGTFSTimeException):
			_ = GT("37:00:00").to_fstr(use_ampm=True)
