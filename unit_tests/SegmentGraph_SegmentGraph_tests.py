from datetime import datetime
from pathlib import Path
import numpy as np
import sys
import unittest


sys.path.insert(0, "../")
from src.PatrolRoutes import GTFS_STRF
from src.PatrolRoutes.Duration import BaseDuration, Hours, Minutes, Seconds
from src.PatrolRoutes.Loop import Loop
from src.PatrolRoutes.PolygonBoundary import PolygonBoundary
from src.PatrolRoutes.Settings import Settings
from src.PatrolRoutes.SegmentGraph import Boundary, SegmentGraph
from src.PatrolRoutes.Utils import Point



class SegmentGraph_SegmentGraph_tests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		## Friars/Pac Hwy
		#cls.northwest = Point((32.7624147116548, -117.20350605999911))

		## Mission Gorge/Princess View
		#cls.northeast = Point((32.80683362786258, -117.0789570681988))

		## SR-54/SR-125
		#cls.southeast = Point((32.754669147398346, -117.00958907807532))

		## Cabrillo monument
		#cls.southwest = Point((32.66805800613335, -117.24076493223097))

		#cls._boundary = Boundary(
		#	cls.northwest,
		#	cls.northeast,
		#	cls.southeast,
		#	cls.southwest
		#)

		#cls.wt = WalkingTransfers.load("wt-core-0.1.pickle", cls._boundary)

		#cls._boundary = PolygonBoundary(Path("examples/midcity_pbound.txt"))

		#cls._sg = SegmentGraph(
		#	"gtfs/MTS_JUN25/",
		#	datetime.strptime("20250722", GTFS_STRF), ## Tuesday
		#	Minutes(10),
		#	Minutes(5),
		#	0.1,
		#	#cls.wt,
		#	boundary = cls._boundary,
		#	transfer_timepoint_only = True
		#)

		cls._settings = Settings(
			Path("examples/midcity_settings_20250806.json")
		)

		cls._sg = SegmentGraph(cls._settings)
		
		cls._sg.build_graph()

		rng = np.random.default_rng(seed = 49)

		while True:
			one_loop = Loop(
				1, 
				rng.integers(low = 1, high = int(1e16)), 
				cls._sg, 
				cls._settings
			)

			one_loop.build()

			print(str(one_loop))

			_ = input("build next loop?")

	def test_placeholder(self):
		self.assertEqual(1, 1)