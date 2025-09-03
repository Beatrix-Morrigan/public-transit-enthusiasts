import sys
import unittest


sys.path.insert(0, "../")
from src.PatrolRoutes.SegmentGraph import Boundary
from src.PatrolRoutes.Utils import Point



class SegmentGraph_Boundary_tests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		## Friars/PacHwy - Mission Gorge / Princess View - SR-54/SR-125 - SR-54/I-5

		## Friars/Pac Hwy
		cls.northwest = Point((32.7624147116548, -117.20350605999911))

		## Mission Gorge/Princess View
		cls.northeast = Point((32.80683362786258, -117.0789570681988))

		## SR-54/SR-125
		cls.southeast = Point((32.754669147398346, -117.00958907807532))

		## Cabrillo monument
		cls.southwest = Point((32.66805800613335, -117.24076493223097))

		cls.boundary = Boundary(
			cls.northwest,
			cls.northeast,
			cls.southeast,
			cls.southwest
		)

		cls.i15_i8 = Point((32.77871464626797, -117.11236615623476))
		#cls.nharbor_harborisland = Point((32.729385509641595, -117.1950638046493))
		cls.nimitz_i8 = Point((32.75421602619531, -117.23748241680231))

	def test_contains(self):
		self.assertTrue(self.boundary.contains(self.i15_i8))

		self.assertFalse(self.boundary.contains(self.nimitz_i8))