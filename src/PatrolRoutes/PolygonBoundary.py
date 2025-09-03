"""
Generalization of `Boundary` to any closed, not-self-intersecting shape for
drawing more precise neighborhood map boundaries.

Uses following sources for intersection/contains algorithms
- https://www.eecs.umich.edu/courses/eecs380/HANDOUTS/PROJ2/InsidePoly.html
- https://stackoverflow.com/questions/4449110/python-solve-equation-for-one-variable
"""


from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
import numpy as np
from sympy import Symbol, Eq, solve
from typing import Generic, Iterator, List, Literal, Optional, overload, Tuple, TypeVar
from typing_extensions import Self


from .Utils import Point


class PolygonPoint(Point):
	_ln: Optional["PolygonPoint"]
	_rn: Optional["PolygonPoint"]
	_info: Optional[str]

	def __init__(
		self,
		lat_lon: Tuple[float, float],
		info: Optional[str] = None
	) -> None:
		"""
		"""
		super().__init__(lat_lon)

		self._ln = None
		self._rn = None
		self._info = info

	def __repr__(self) -> str:
		return f"PolygonPoint(lat={self._lat}, lon={self._lon})"

	def __str__(self) -> str:
		"""
		"""
		base = f"({self._lat}, {self._lon}"
		
		if self._info is not None:
			base += f"; {self._info}"

		return base + ')'

	@property
	def left_neighbor(self) -> "PolygonPoint":
		"""
		"""
		if self._ln is None:
			raise RuntimeError(
				f"Cannot retrieve left neighbor from point {self}, must be set first."
			)
		return self._ln
	
	@left_neighbor.setter
	def left_neighbor(
		self,
		pt: "PolygonPoint"
	) -> None:
		"""
		"""
		self._ln = pt
	
	@property
	def right_neighbor(self) -> "PolygonPoint":
		"""
		"""
		if self._rn is None:
			raise RuntimeError(
				f"Cannot retrieve right neighbor from point {self}, must be set first."
			)
		return self._rn
	
	@right_neighbor.setter
	def right_neighbor(
		self,
		pt: "PolygonPoint"
	) -> None:
		"""
		"""
		self._rn = pt


class Polygon:
	_pts: List[PolygonPoint]
	
	def __init__(
		self,
		boundary_file_path: Path
	) -> None:
		"""
		"""
		pts = self._parse_boundary_file(boundary_file_path)

		n_pts = len(pts)

		for i, pt in enumerate(pts):
			ln_indx = (i - 1) % n_pts
			rn_indx = (i + 1) % n_pts

			pt.left_neighbor = pts[ln_indx]
			pt.right_neighbor = pts[rn_indx]

		self._pts = pts

	def __getitem__(
		self,
		key: int
	) -> "PolygonPoint":
		"""
		"""
		return self._pts[key]
	
	class InvalidBoundaryPointError(Exception):
		def __init__(
			self,
			path: Path,
			line_num: int,
			line: str
		) -> None:
			"""
			"""
			super().__init__(
				f"Invalid boundary point in {path}, line {line_num}: '{line}'"
			)

	def _parse_boundary_file(
		self,
		boundary_file_path: Path,
	) -> List[PolygonPoint]:
		"""
		"""
		pts: List[PolygonPoint] = []

		with open(boundary_file_path, 'r') as f:
			pb_lines = f.readlines()

		for i, line in enumerate(pb_lines):
			tokens = line.strip('\n').strip().split('#')

			uncommented = tokens[0]

			try:
				commented = ''.join(tokens[1:]).strip('#').strip()
			except IndexError:
				commented = None

			if uncommented == '':
				continue

			try:
				lat, lon = list(map(float, uncommented.split(',')))
			except:
				raise self.InvalidBoundaryPointError(
					boundary_file_path, i + 1, line
				)
			
			pts.append(
				PolygonPoint(
					(lat, lon),
					info = commented
				)
			)
		
		return pts
	
	def furthest_east_lon(self) -> float:
		"""
		For building cross-shape rays to check number of intersections
		"""
		return max([
			p.lon for p in self._pts
		])
	
	def iter_lines(self) -> "Iterator[LineSegment]":
		"""
		"""
		for i in range(self.n_points):
			yield LineSegment.new_line_segment(
				self._pts[i],
				self._pts[i].right_neighbor
			)

	@property
	def n_points(self) -> int: return len(self._pts)


PT1_T = TypeVar("PT1_T", bound = "Point")
PT2_T = TypeVar("PT2_T", bound = "Point")
class LineSegment(ABC, Generic[PT1_T, PT2_T]):
	"""
	Base for line segment - specialty classes for 
	vertical/horizontal/other lines. In all cases
	where line segments represent a ray or directed path,
	`_pt1` will be considered the origin point. 
	"""
	_pt1: PT1_T
	_pt2: PT2_T

	@abstractmethod
	def __init__(
		self,
		point1: PT1_T,
		point2: PT2_T
	) -> None:
		pass

	def __str__(self) -> str:
		"""
		"""
		return f"[{self.p1}----{self.p2}]"
	
	def __repr__(self) -> str:
		return f"{self.__class__.__name__}({self._pt1!r}, {self._pt2!r})"
	
	def __eq__(
		self,
		other: object
	) -> bool:
		"""
		"""
		if not isinstance(other, LineSegment):
			return False
		
		return (self._pt1 == other._pt1) and (self._pt2 == other._pt2)

	@classmethod
	def makes_horizontal_line(
		cls,
		point1: Point,
		point2: Point
	) -> bool:
		"""
		"""
		return point1.lat == point2.lat
	
	@classmethod
	def makes_vertical_line(
		cls,
		point1: Point,
		point2: Point
	) -> bool:
		"""
		"""
		return point1.lon == point2.lon

	NEW_PT1_T = TypeVar("NEW_PT1_T", bound = "Point")
	NEW_PT2_T = TypeVar("NEW_PT2_T", bound = "Point")
	@classmethod
	def new_line_segment(
		cls,
		point1: NEW_PT1_T,
		point2: NEW_PT2_T
	) -> "LineSegment[NEW_PT1_T, NEW_PT2_T]":
		"""
		"""
		if cls.makes_horizontal_line(point1, point2):
			return _HorizontalLineSegment(point1, point2)
		elif cls.makes_vertical_line(point1, point2):
			return _VerticalLineSegment(point1, point2)
		else:
			return _LineSegment(point1, point2)
		
	@property
	def p1(self) -> PT1_T: return self._pt1

	@property
	def p2(self) -> PT2_T: return self._pt2
		
	@property
	@abstractmethod
	def slope(self) -> float|None:
		pass

	@property
	@abstractmethod
	def intercept(self) -> float|None:
		pass

	@property
	def magnitude(self) -> float:
		"""
		"""
		if not self.is_origin_vector():
			comp_vec = self.to_origin_vector()
		else:
			comp_vec = self

		return np.sqrt(
			(comp_vec._pt2[0]**2) + (comp_vec._pt2[1]**2)
		)
	
	def to_origin_vector(self) -> "LineSegment[PT1_T, PT2_T]":
		"""
		"""
		new_pt1 = self._pt1._copy_and_update_position((0.0, 0.0))
		new_pt2 = self._pt2._copy_and_update_position((
			self._pt2.lat - self._pt1.lat,
			self._pt2.lon - self._pt1.lon
		))

		return self.__class__(new_pt1, new_pt2)
	
	def is_origin_vector(self) -> bool:
		"""
		"""
		return self._pt1 == Point((0, 0))

	def latitude_in_range(
		self,
		lat: float
	) -> bool:
		"""
		Return `True` if the provided value falls between this line segment's
		latitude span.
		"""
		return (
			(self.p1.lat <= lat <= self.p2.lat)
			or (self.p2.lat <= lat <= self.p1.lat)
		)
	
	def longitude_in_range(
		self,
		lon: float
	) -> bool:
		"""
		Return `True` if the provided value falls between this line segment's
		longitude span.
		"""
		return (
			(self.p1.lon <= lon <= self.p2.lon)
			or (self.p2.lon <= lon <= self.p1.lon)
		)

	@abstractmethod
	def interp_lat(
		self,
		lon: float
	) -> Optional[float]:
		"""
		Returns `None` if interpolation is undefined or not unique.
		"""
		pass

	@abstractmethod
	def interp_lon(
		self,
		lat: float
	) -> Optional[float]:
		"""
		Returns `Non` if interpolation is undefined or not unique.
		"""
		pass

	@abstractmethod
	def intersects(
		self,
		other: "LineSegment"
	) -> bool: 
		pass

	PROJ_PTYPE = TypeVar("PROJ_PTYPE", bound = Point)
	@overload
	def project_point(
		self,
		point: PROJ_PTYPE,
		*,
		bounded: Literal[False]
	) -> PROJ_PTYPE: ...
	@overload
	def project_point(
		self,
		point: PROJ_PTYPE,
		*,
		bounded: bool = True
	) -> Optional[PROJ_PTYPE]: ...
	def project_point(
		self,
		point: PROJ_PTYPE,
		bounded: bool = True
	) -> Optional[PROJ_PTYPE]:
		"""
		"""
		s = self._pt2
		v = point

		res = ((v @ s) / (s @ s)) @ s

		if bounded:
			if (not self.latitude_in_range(res.lat)) or (not self.longitude_in_range(res.lon)):
				return None

		return point._copy_and_update_position((res.lat, res.lon))
	
	def get_angle_with(
		self,
		point: "Point"
	) -> float:
		"""
		"""
		other_lseg = self.new_line_segment(
			self._pt1,
			point
		)

		self_vec = self.to_origin_vector()
		other_vec = other_lseg.to_origin_vector()

		## https://wumbo.net/formulas/angle-between-two-vectors-2d/

		v1 = self_vec._pt2.lon
		v2 = self_vec._pt2.lat
		w1 = other_vec._pt2.lon
		w2 = other_vec._pt2.lat

		return -1 * np.degrees(np.arctan2(
			(v1 * w2) - (v2 * w1),
			(v1 * w1) + (v2 * w2)
		))


class _HorizontalLineSegment(LineSegment):
	"""
	Constant latitude, slope == 0.

			/
	----------------
		/

	"""
	def __init__(
		self,
		point1: Point,
		point2: Point
	) -> None:
		"""
		"""
		if point1.lat != point2.lat:
			raise ValueError(
				f"Line formed by {point1} and {point2} is not horizontal."
			)
		
		self._pt1 = point1
		self._pt2 = point2

	@property
	def slope(self) -> float: return 0.0

	@property
	def intercept(self) -> float: return self._pt1.lat

	def interp_lat(
		self,
		lon: float
	) -> Optional[float]:
		"""
		"""
		if self.longitude_in_range(lon):
			return self._pt1.lat
		return None
	
	def interp_lon(
		self,
		lat: float
	) -> None:
		"""
		"""
		return None
	
	def intersects(
		self,
		other: LineSegment
	) -> bool:
		"""
		"""
		candidate_intersection_lon = other.interp_lon(self._pt1.lat)

		if candidate_intersection_lon is None:
			return False

		return self.longitude_in_range(candidate_intersection_lon)
	

class _VerticalLineSegment(LineSegment):
	"""
	Constant longitude, slope is `None`.

		|
		|/
	   /|
	  /	|
		|
		|

	"""
	def __init__(
		self,
		point1: Point,
		point2: Point
	) -> None:
		"""
		"""
		if point1.lon != point2.lon:
			raise ValueError(
				f"Line formed by {point1} and {point2} is not vertical."
			)
		
		self._pt1 = point1
		self._pt2 = point2

	@property
	def slope(self) -> None: return None

	@property
	def intercept(self) -> None: return None

	def interp_lat(
		self,
		lon: float
	) -> None:
		"""
		"""
		return None
	
	def interp_lon(
		self,
		lat: float
	) -> Optional[float]:
		"""
		"""
		if self.latitude_in_range(lat):
			return self._pt1.lon
		return None
	
	def intersects(
		self,
		other: LineSegment
	) -> bool:
		"""
		"""
		candidate_intersection_lat = other.interp_lat(self._pt1.lon)

		if candidate_intersection_lat is None:
			return False
		
		return self.latitude_in_range(candidate_intersection_lat)


class _LineSegment(LineSegment):
	"""
	Any line that isn't vertical or horizontal.
	"""
	def __init__(
		self,
		point1: Point,
		point2: Point
	) -> None:
		"""
		"""
		if self.makes_horizontal_line(point1, point2):
			raise ValueError(
				f"_HorizontalLine instance is needed to represent a horizontal "
				f"line. "
				f"Use LineSegment.new_line_segment() to automatically create "
				f"instances of "
				f"the correct LineSegment type."
			)
		
		if self.makes_vertical_line(point1, point2):
			raise ValueError(
				f"_VerticalLine instance is needed to represent a vertical "
				f"line. "
				f"Use LineSegment.new_line_segment() to automatically create "
				f"instances of "
				f"the correct LineSegment type."
			)
		
		self._pt1 = point1
		self._pt2 = point2

	@property
	def slope(self) -> float:
		"""
		Change in longitude (x) over change in latitude (y).
		"""
		return (
			(self.p2.lat - self.p1.lat) 
			/ (self.p2.lon - self.p1.lon)
		)

	@property
	def intercept(self) -> float:
		"""
		y - y1 = m(x - x1)
		y = m(- x1) + y1
		y = -x1*m + y1
		"""
		return -(self._pt1.lon*self.slope) + self._pt1.lat
	
	def interp_lat(
		self,
		lon: float
	) -> Optional[float]:
		"""
		lat = m*lon + b
		"""
		if not self.longitude_in_range(lon):
			return None

		lat = (self.slope*lon) + self.intercept

		if not self.latitude_in_range(lat):
			return None
		
		return lat
	
	def interp_lon(
		self,
		lat: float
	) -> Optional[float]:
		"""
		lat = m*lon + b
		lat - b = m*lon
		(lat -b) / m = lon
		"""
		if not self.latitude_in_range(lat):
			return None

		lon = (lat - self.intercept) / self.slope

		if not self.longitude_in_range(lon):
			return None
		
		return lon
	
	def intersects(
		self,
		other: LineSegment
	) -> bool:
		"""
		y = m1*x + b1
		y = m2*x + b2

		m1*x + b1 = m2*x + b2

		(m1 - m2)*x + (b1-b2) = 0
		"""
		if isinstance(other, _HorizontalLineSegment|_VerticalLineSegment):
			return other.intersects(self)
		
		assert isinstance(other, _LineSegment) #for type hinting mostly

		x = Symbol('x')
		m1 = self.slope
		b1 = self.intercept

		m2 = other.slope
		b2 = other.intercept

		try:
			candidate_lon: float = solve((x*(m1-m2)) + (b1-b2), x)[0] #type: ignore
		except IndexError:
			return False

		on_self = self.interp_lat(candidate_lon)
		on_other = self.interp_lat(candidate_lon)

		return not ((on_self is None) or (on_other is None))


class PolygonBoundary:
	_p: Polygon

	def __init__(
		self,
		boundary_file_path: Path
	) -> None:
		"""
		"""
		self._p = Polygon(boundary_file_path)

	def __eq__(
		self,
		other: object
	) -> bool:
		"""
		"""
		if not isinstance(other, PolygonBoundary):
			return False
		
		if self._p.n_points != other._p.n_points:
			return False
		
		for i in range(self._p.n_points):
			if self._p._pts[i] != other._p._pts[i]:
				return False
			
		return True

	def _get_horizontal_ray(
		self,
		point: Point
	) -> _HorizontalLineSegment:
		"""
		"""
		ray = LineSegment.new_line_segment(
			point,
			Point((point.lat, self._p.furthest_east_lon() + 1e-5))
		)

		if not isinstance(ray, _HorizontalLineSegment):
			raise RuntimeError(
				f"Problem with LineSegment.new_line_segment(), should always "
				f"create a _HorizontalLineSegment in "
				f"PolygonBoundary._get_horizontal_ray()"
			)
		
		return ray

	def contains(
		self,
		other: "Point"
	) -> bool:
		"""
		https://www.eecs.umich.edu/courses/eecs380/HANDOUTS/PROJ2/InsidePoly.html
		"""
		n_intersects = 0

		ray = self._get_horizontal_ray(other)

		for line in self._p.iter_lines():
			if ray.intersects(line):
				n_intersects += 1

		return (n_intersects > 0) and (n_intersects % 2 == 1)