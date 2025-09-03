from pathlib import Path
import sys
import unittest

sys.path.insert(0, "../")

from src.PatrolRoutes.PolygonBoundary import (
	PolygonPoint, Polygon, PolygonBoundary, LineSegment,
	_HorizontalLineSegment, _LineSegment, _VerticalLineSegment
)
from src.PatrolRoutes.Utils import Point


class PolygonBoundary_PolygonBoundary_tests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls._p = Polygon(Path("examples/midcity_pbound.txt"))
		cls._pb = PolygonBoundary(Path("examples/midcity_pbound.txt"))

	def test_polygon_point_neighbors(self):
		"""
		"""
		self.assertIs(
			self._p[0].right_neighbor,
			self._p[1]
		)

		self.assertIs(
			self._p[1].left_neighbor,
			self._p[0]
		)

		self.assertIs(
			self._p[0].left_neighbor,
			self._p[self._p.n_points-1]
		)

		self.assertIs(
			self._p[self._p.n_points-1].right_neighbor,
			self._p[0]
		)

	def test_polygon_point_str(self):
		"""
		"""
		self.assertEqual(
			str(self._p[0]),
			"(32.76298497509194, -117.1467387655267; Park & Adams)"
		)

	def test_furthest_east_lon(self):
		"""
		"""
		self.assertEqual(
			self._p.furthest_east_lon(),
			-117.00973276277968
		)

	def test_line_slope_intercept(self):
		line = LineSegment.new_line_segment(
			Point((0, 0)),
			Point((1, 1))
		)
		self.assertEqual(line.slope, 1.0)
		self.assertEqual(line.intercept, 0)

		hline = LineSegment.new_line_segment(
			Point((1, 1)),
			Point((1, 4))
		)
		self.assertIsInstance(hline, _HorizontalLineSegment)
		self.assertEqual(hline.slope, 0)
		self.assertEqual(hline.intercept, 1)

		vline = LineSegment.new_line_segment(
			Point((1, 1)),
			Point((4, 1))
		)
		self.assertIsInstance(vline, _VerticalLineSegment)
		self.assertIsNone(vline.slope)
		self.assertIsNone(vline.intercept)

	def test_lat_lon_in_range(self):
		line = LineSegment.new_line_segment(
			Point((0, 0)),
			Point((1, 1))
		)
		self.assertTrue(line.latitude_in_range(0.5))
		self.assertTrue(line.longitude_in_range(0.5))
		self.assertFalse(line.latitude_in_range(1.5))
		self.assertFalse(line.longitude_in_range(1.5))

	def test_interp(self):
		line = LineSegment.new_line_segment(
			Point((0, 0)),
			Point((1, 1))
		)
		self.assertEqual(line.interp_lat(0.5), 0.5)
		self.assertEqual(line.interp_lon(0.5), 0.5)
		self.assertIsNone(line.interp_lat(1.5))
		self.assertIsNone(line.interp_lon(1.5))

	def test_intersect_line_line(self):
		line1 = LineSegment.new_line_segment(
			Point((0, 0)),
			Point((1, 1))
		)
		line2 = LineSegment.new_line_segment(
			Point((1, 0)),
			Point((0, 1))
		)

		self.assertTrue(line1.intersects(line2))

		line3 = LineSegment.new_line_segment(
			Point((3, 3)),
			Point((4, 4))
		)

		self.assertFalse(line3.intersects(line1))
		self.assertFalse(line3.intersects(line2))

	def test_intersect_line_hline(self):
		line1 = LineSegment.new_line_segment(
			Point((0, 0)),
			Point((1, 1))
		)
		hline1 = LineSegment.new_line_segment(
			Point((0.5, 0.0)),
			Point((0.5, 0.5))
		)
		self.assertIsInstance(hline1, _HorizontalLineSegment)

		self.assertEqual(line1.interp_lon(hline1.p1.lat), 0.5)
		self.assertTrue(hline1.longitude_in_range(0.5))
		self.assertTrue(line1.intersects(hline1))

		self.assertTrue(hline1.intersects(line1))

		hline2 = LineSegment.new_line_segment(
			Point((3.5, 0.0)),
			Point((3.5, 0.5))
		)

		self.assertFalse(hline2.intersects(line1))

	def test_intersect_line_vline(self):
		line1 = LineSegment.new_line_segment(
			Point((0, 0)),
			Point((1, 1))
		)

		vline1 = LineSegment.new_line_segment(
			Point((0.0, 0.5)),
			Point((0.5, 0.5))
		)
		self.assertIsInstance(vline1, _VerticalLineSegment)

		self.assertTrue(vline1.intersects(line1))
		self.assertTrue(line1.intersects(vline1))

		vline2 = LineSegment.new_line_segment(
			Point((5.0, 0.5)),
			Point((7.0, 0.5))
		)
		self.assertFalse(vline2.intersects(line1))

	def test_contains(self):
		"""
		"""
		## University & Park Blvd

		## ray is [(32.74840537087931, -117.14624808138211)----(32.74840537087931, -117.00973276267968)]
		## should intersect 

		ray = LineSegment.new_line_segment(
			Point((32.74840537087931, -117.14624808138211)),
			Point((32.74840537087931, -117.00973276267968))
		)

		bound_line = LineSegment.new_line_segment(
			Point((32.753485080627335,-117.01159987216715)), ## Spring St & SR-125/SR-94
			Point((32.70497761595613,-117.00973276277968)) ## SR-125 & Jamacha
		)

		self.assertIsInstance(ray, _HorizontalLineSegment)

		self.assertIsInstance(bound_line, _LineSegment)

		self.assertTrue(bound_line.latitude_in_range(ray.p1.lat))

		self.assertIsNotNone(bound_line.interp_lon(ray.p1.lat))

		self.assertTrue(ray.intersects(bound_line))
		
		self.assertTrue(
			self._pb.contains(
				Point((32.74840537087931, -117.14624808138211))
			)
		)

		## OTTC
		self.assertFalse(
			self._pb.contains(
				Point((32.75497455840468, -117.19977489323054))
			)
		)

		## City College
		self.assertTrue(
			self._pb.contains(
				Point((32.716522765620944, -117.15420037766869))
			)
		)

		## SR-125 & I-8
		self.assertFalse(
			self._pb.contains(
				Point((32.777965809907315, -117.00372980168846))
			)
		)

		## 28th & Commercial
		self.assertTrue(
			self._pb.contains(
				Point((32.705389774464024, -117.13389464675244))
			)
		)

	def test_proj_point(self):
		## https://en.wikibooks.org/wiki/Linear_Algebra/Orthogonal_Projection_Onto_a_Line
		new_pt = Point((2, 3))

		line_seg = LineSegment.new_line_segment(
			Point((0, 0)),
			Point((2, 4))
		)

		self.assertEqual(
			line_seg.project_point(new_pt),
			Point((1.6, 3.2))
		)

	def test_proj_point_limit(self):
		## https://en.wikibooks.org/wiki/Linear_Algebra/Orthogonal_Projection_Onto_a_Line
		new_pt = Point((20, 30))

		line_seg = LineSegment.new_line_segment(
			Point((0, 0)),
			Point((1, 2))
		)

		self.assertIsNone(line_seg.project_point(new_pt))


	def test_origin_vector_lseg(self):
		lseg = LineSegment.new_line_segment(
			Point((4, 8)),
			Point((8, 16))
		)

		expected_vec = _LineSegment(
			Point((0, 0)),
			Point((4, 8))
		)

		self.assertEqual(lseg.to_origin_vector(), expected_vec)

	def test_origin_vector_lseg_offcenter(self):
		lseg = LineSegment.new_line_segment(
			Point((0, 3)),
			Point((1, 6))
		)

		expected_vec = _LineSegment(
			Point((0, 0)),
			Point((1, 3))
		)

		self.assertEqual(lseg.to_origin_vector(), expected_vec)

	def test_origin_vector_vertical(self):
		vseg = LineSegment.new_line_segment(
			Point((1, 4)),
			Point((3, 4))
		)

		expected_vec = _VerticalLineSegment(
			Point((0, 0)),
			Point((2, 0))
		)

		self.assertEqual(vseg.to_origin_vector(), expected_vec)

	def test_origin_vector_horizontal(self):
		hseg = LineSegment.new_line_segment(
			Point((1, 4)),
			Point((1, 6))
		)

		expected_vec = _HorizontalLineSegment(
			Point((0, 0)),
			Point((0, 2))
		)

		self.assertEqual(hseg.to_origin_vector(), expected_vec)

	def test_get_angle_with_lseg(self):
		lseg = LineSegment.new_line_segment(
			Point((2.0, 2.0)), Point((4.0, 4.0))
		)

		point = Point((3.0, 1.0))

		self.assertEqual(
			round(lseg.get_angle_with(point), 2),
			-90.00
		)

	def test_get_angle_with_vseg(self):
		vseg = LineSegment.new_line_segment(
			Point((2.0, 2.0)), Point((4.0, 2.0))
		)

		point = Point((3.0, 3.0))

		self.assertEqual(
			round(vseg.get_angle_with(point), 2),
			45.00
		)

		point2 = Point((1.0, 3.0))

		self.assertEqual(
			round(vseg.get_angle_with(point2), 2),
			135.00
		)

		point3 = Point((3.0, 1.0))

		self.assertEqual(
			round(vseg.get_angle_with(point3), 2),
			-45.00
		)

	def test_get_angle_with_hseg(self):
		hseg = LineSegment.new_line_segment(
			Point((2.0, 2.0)), Point((2.0, 4.0))
		)

		point = Point((3.0, 3.0))

		self.assertEqual(
			round(hseg.get_angle_with(point), 2),
			-45.00
		)

		point2 = Point((1.0, 3.0))

		self.assertEqual(
			round(hseg.get_angle_with(point2), 2),
			45.00
		)

		point3 = Point((3.0, 1.0))

		self.assertEqual(
			round(hseg.get_angle_with(point3), 2),
			-135.00
		)