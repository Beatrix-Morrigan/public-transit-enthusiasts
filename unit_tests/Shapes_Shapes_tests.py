from pathlib import Path
import sys
sys.path.insert(0, "../")
import unittest


from src.PatrolRoutes.Shapes import Shapes


class Shapes_Shapes_tests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls._shapes = Shapes(
			Path("gtfs/MTS_JUN25/shapes.txt")
		)

	def test_loaded_sorted(self):
		shape = self._shapes["105_0_98"]

		self.assertEqual(
			shape[0].shape_
		)