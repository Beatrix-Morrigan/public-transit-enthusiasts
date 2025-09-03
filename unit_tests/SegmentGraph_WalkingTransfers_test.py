from pathlib import Path
import sys
import unittest


import sys
sys.path.insert(0, "../")
from src.PatrolRoutes.GTFS import GTFS
from src.PatrolRoutes.SegmentGraph import Boundary, WalkingTransfers
from src.PatrolRoutes.PolygonBoundary import PolygonBoundary
from src.PatrolRoutes.Utils import Point



class SegmentGraph_WalkingTransfers_tests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		#cls._boundary = Boundary(
		#	Point((32.75722565834968, -117.15136039189153)), ## Meade & Maryland
		#	Point((32.75729474651464, -117.12569012380082)), ## Mead & I-805
		#	Point((32.74597566541065, -117.12030708065775)), ## I-805 & Landis
		#	Point((32.746466085284226, -117.15123562300681)) ## Robinson & Richmond
		#)
		cls._boundary = PolygonBoundary(Path("examples/midcity_pbound.txt"))

		cls._gtfs = GTFS(Path("gtfs/MTS_JUN25/"))

		cls._wt = WalkingTransfers(
			[
				stop for stop in cls._gtfs.stops
				if cls._boundary.contains(stop.stop_point)
			],
			cls._boundary,
			0.1
		)

	#def test_load(self):
	#	loaded_wt = WalkingTransfers.load("examples/wt_hc-np.pickle", self._boundary)
	#
	#	self.assertEqual(
	#		self._wt._boundary,
	#		loaded_wt._boundary
	#	)

	#def test_load_bad_boundary(self):
	#	bad_boundary = Boundary(
	#		Point((0, 0)), Point((1, 1)), 
	#		Point((1, 2)), Point((2, 2))
	#	)
	#
	#	with self.assertWarns(Warning):
	#		WalkingTransfers.load("examples/wt_hc-np.pickle", bad_boundary)