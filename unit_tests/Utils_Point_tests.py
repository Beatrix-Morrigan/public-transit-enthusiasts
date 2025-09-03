import sys
import unittest


sys.path.insert(0, "../")
from src.PatrolRoutes.Utils import Point


class Utils_Point_tests(unittest.TestCase):
	"""
	Uses GeoPy's examples:
		https://geopy.readthedocs.io/en/stable/
	"""
	@classmethod
	def setUpClass(cls):
		"""
		"""
		cls.newport_ri = Point((41.49008, -71.312796))
		cls.cleveland = Point((41.499498, -81.695391))

		## Friars/PacHwy - Mission Gorge / Princess View - SR-54/SR-125 - SR-54/I-5

		## Friars/Pac Hwy
		cls.northwest = Point((32.7624147116548, -117.20350605999911))

		## Mission Gorge/Princess View
		cls.northeast = Point((32.80683362786258, -117.0789570681988))

		## SR-54/SR-125
		cls.southeast = Point((32.754669147398346, -117.00958907807532))

		## Cabrillo monument
		cls.southwest = Point((32.66805800613335, -117.24076493223097))

		cls.i15_i8 = Point((32.77871464626797, -117.11236615623476))

		#cls.nharbor_harborisland = Point((32.729385509641595, -117.1950638046493))

	def test_subset(self):
		self.assertEqual(
			self.newport_ri[0],
			41.49008
		)

		self.assertEqual(
			self.cleveland[1],
			-81.695391
		)

		with self.assertRaises(IndexError):
			self.newport_ri[2] #type: ignore

	def test_distance(self):
		#self.assertEqual(
		#	round(
		#		self.newport_ri.distance_to(self.cleveland, dist_unit = "mi"),
		#		2
		#	),
		#	538.39
		#)

		with self.assertRaises(ValueError):
			self.newport_ri.distance_to(
				self.cleveland, dist_unit = "absolute_unit"
			)

	def test_is_north_of(self):
		self.assertTrue(
			self.i15_i8.is_north_of(self.southeast)
		)

	def test_is_south_of(self):
		self.assertTrue(
			self.i15_i8.is_south_of(self.northeast)
		)

	def test_is_east_of(self):
		self.assertTrue(
			self.i15_i8.is_east_of(self.southwest)
		)

	def test_is_west_of(self):
		self.assertTrue(
			self.i15_i8.is_west_of(self.northeast)
		)

	def test_furthest_north(self):
		self.assertIs(
			Point.furthest_north([self.northeast, self.northwest]),
			self.northeast
		)

	def test_furthest_south(self):
		self.assertIs(
			Point.furthest_south([self.southeast, self.southwest]),
			self.southwest
		)

	def test_furthest_east(self):
		self.assertIs(
			Point.furthest_east([self.northeast, self.southeast]),
			self.southeast
		)

	def test_furthest_west(self):
		self.assertIs(
			Point.furthest_west([self.northwest, self.southwest]),
			self.southwest
		)

	def test_get_slope(self):
		self.assertEqual(
			round(Point.get_slope(self.southwest, self.northwest), 2),
			2.53
		)

	def test_interp_lat(self):
		self.assertEqual(
			Point.interp_lat(
				Point((8, 4)),
				Point((2, 1)),
				2
			),
			4
		)

	def test_interp_lon(self):
		self.assertEqual(
			Point.interp_lon(
				Point((8, 4)),
				Point((2, 1)),
				4
			),
			2
		)

	def test_is_east_of_line(self):
		"""
		"""
		self.assertTrue(
			self.i15_i8.is_east_of_line(
				self.southwest,
				self.northwest
			)
		)

		self.assertTrue(
			self.i15_i8.is_east_of_line(
				self.northwest,
				self.southwest
			)
		)

		self.assertFalse(
			self.i15_i8.is_east_of_line(
				self.northeast,
				self.southeast
			)
		)

		self.assertFalse(
			self.i15_i8.is_east_of_line(
				self.southeast,
				self.northeast
			)
		)

	def test_is_west_of_line(self):
		"""
		"""
		self.assertTrue(
			self.i15_i8.is_west_of_line(
				self.southeast,
				self.northeast
			)
		)

		self.assertTrue(
			self.i15_i8.is_west_of_line(
				self.northeast,
				self.southeast
			)
		)

		self.assertFalse(
			self.i15_i8.is_west_of_line(
				self.northwest,
				self.southwest
			)
		)

		self.assertFalse(
			self.i15_i8.is_west_of_line(
				self.southwest,
				self.northwest
			)
		)

	def test_is_north_of_line(self):
		"""
		"""
		self.assertTrue(
			self.i15_i8.is_north_of_line(
				self.southeast,
				self.southwest
			)
		)

		self.assertTrue(
			self.i15_i8.is_north_of_line(
				self.southwest,
				self.southeast
			)
		)

		self.assertFalse(
			self.i15_i8.is_north_of_line(
				self.northwest,
				self.northeast
			)
		)

		self.assertFalse(
			self.i15_i8.is_north_of_line(
				self.northeast,
				self.northwest
			)
		)

	def test_is_south_of_line(self):
		"""
		"""
		self.assertTrue(
			self.i15_i8.is_south_of_line(
				self.northeast,
				self.northwest
			)
		)

		self.assertTrue(
			self.i15_i8.is_south_of_line(
				self.northwest,
				self.northeast
			)
		)

		self.assertFalse(
			self.i15_i8.is_south_of_line(
				self.southeast,
				self.southwest
			)
		)

		self.assertFalse(
			self.i15_i8.is_south_of_line(
				self.southwest,
				self.southeast
			)
		)

	def test_dot_product(self):
		self.assertEqual(
			Point((3, 4)) @ Point((4, 3)),
			24.0
		)

		self.assertEqual(
			Point((3, 4)) @ 2,
			Point((6, 8))
		)

		self.assertEqual(
			2 @ Point((3, 4)),
			Point((6, 8))
		)

		## All examples below from https://en.wikibooks.org/wiki/Linear_Algebra/Orthogonal_Projection_Onto_a_Line

		self.assertEqual(
			Point((2, 3)) @ Point((1, 2)),
			8
		)

		self.assertEqual(
			Point((1, 2)) @ Point((1, 2)),
			5
		)

		self.assertEqual(
			(8./5.) @ Point((1, 2)),
			Point((1.6, 3.2))
		)