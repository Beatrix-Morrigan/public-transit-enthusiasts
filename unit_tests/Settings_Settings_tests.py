from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, "../")
import unittest


from src.PatrolRoutes.Settings import Settings


class Settings_Settings_tests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls._s = Settings(Path("examples/midcity_settings_20250806.json"))

	def test_route_excluded(self):
		self.assertTrue(self._s.route_is_excluded("992"))
		self.assertFalse(self._s.route_is_excluded("41"))

	def test_mask_route(self):
		self.assertEqual(
			f"Route {self._s.mask_route('510')} to UTC.",
			f"Route Blue Line to UTC."
		)

		self.assertEqual(
			f"Route {self._s.mask_route('41')} to UCSD.",
			f"Route 41 to UCSD."
		)

	def test_all_settings_properties(self):
		self.assertEqual(
			self._s.service_date,
			datetime(year = 2025, month = 8, day = 6)
		)

		#self.