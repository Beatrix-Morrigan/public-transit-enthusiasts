"""
Utility functions.
"""


import copy
from enum import Enum
from geopy.distance import geodesic
from numpy import cos, dot, sqrt
from typing import Any, Dict, Generic, List, Literal, Optional, overload, Tuple, Type, TypeVar, Union
from typing_extensions import Self
import warnings


from .Settings import Settings


class Point:
	_lat: float
	_lon: float

	def __init__(
		self,
		lat_lon: Tuple[float, float]
	) -> None:
		self._lat = lat_lon[0]
		self._lon = lat_lon[1]

	def __repr__(self) -> str:
		return f"Point(lat={self._lat}, lon={self._lon})"

	def __getitem__(
		self, 
		key: Literal[0] | Literal[1]
	) -> float:
		"""
		Give tuple-like behavior. Can also use .lat and .lon properties
		"""
		if key == 0:
			return self._lat
		elif key == 1:
			return self._lon
		else:
			raise IndexError(
				f"Index {key} out of bounds for latitude/longitude pair."
			) 
		
	def __eq__(
		self,
		other: object
	) -> bool:
		"""
		"""
		if isinstance(other, Point):
			return (
				(self.lat == other.lat)
				and (self.lon == other.lon)
			)
		else:
			return False
	
	def __str__(self) -> str:
		"""
		"""
		return f"({self._lat}, {self._lon})"
	
	def __add__(self, other: "Point") -> Self:
		"""
		"""
		new_lat_lon = ((
			self._lat + other._lat,
			self._lon + other._lon
		))

		return self._copy_and_update_position(new_lat_lon)

	def __sub__(self, other: "Point") -> Self:
		"""
		"""
		new_lat_lon = ((
			self._lat - other._lat,
			self._lon - other._lon
		))

		return self._copy_and_update_position(new_lat_lon)
	
	@overload
	def __matmul__(self, other: "Point") -> float: ...
	@overload
	def __matmul__(self, other: float|int) -> "Self": ...
	def __matmul__(self, other: "Point|float") -> "Self|float":
		"""
		"""
		ptup = (self.lat, self.lon)

		if isinstance(other, Point):
			return float(dot(ptup, (other.lat, other.lon)))
		else:
			res: Tuple[float, float] = dot(ptup, other)
			return self._copy_and_update_position(res)	

	@overload
	def __rmatmul__(self, other: "Point") -> float: ...
	@overload
	def __rmatmul__(self, other: float|int) -> "Self": ...
	def __rmatmul__(self, other: "Point|float") -> "Self|float":
		"""
		"""
		ptup = (self.lat, self.lon)

		if isinstance(other, Point):
			return float(dot(ptup, (other.lat, other.lon)))
		else:
			res: Tuple[float, float] = dot(ptup, other)
			return self._copy_and_update_position(res)	
	
	POINT_T = TypeVar("POINT_T", bound = "Point")
	def _copy_and_update_position(
		self: POINT_T,
		new_lat_lon: Tuple[float, float]
	) -> POINT_T:
		"""
		"""
		## no deep copy because they sometimes have refs to GTFS objs, etc.
		new_pt = copy.copy(self) 

		new_pt._lat = new_lat_lon[0]
		new_pt._lon = new_lat_lon[1]

		return new_pt

	def distance_to(
		self,
		other: "Point",
		dist_unit: str = "mi"
	) -> float:
		"""
		Either euclidean or geodesic distance. 
		"""
		dist = geodesic(self.tuple, other.tuple)

		if dist_unit == "mi":
			#return dist.miles

			## Use fast version
			## degree conversion: 68.9722
			## https://jonisalonen.com/2014/computing-distance-between-coordinates-can-be-simple-and-fast/

			deglen = 68.9722
			x = other.lat - self.lat
			y = (other.lon - self.lon) * cos(self.lon)
			return deglen * sqrt(x*x + y*y)

		#elif dist_unit == "km":
		#	return dist.km
		#elif dist_unit == "m":
		#	return dist.m
		else:
			raise ValueError(
				f"dist_unit must be 'mi', 'km', or 'm', got '{dist_unit}'."
			)
		
	def is_north_of(
		self,
		other: "Point"
	) -> bool:
		"""
		"""
		return self.lat > other.lat
	
	def is_south_of(
		self,
		other: "Point"
	) -> bool: 
		"""
		"""
		return self.lat < other.lat
	
	def is_east_of(
		self,
		other: "Point"
	) -> bool:
		"""
		"""
		return self.lon > other.lon
	
	def is_west_of(
		self,
		other: "Point"
	) -> bool:
		"""
		"""
		return self.lon < other.lon
	
	@classmethod
	def furthest_north(
		cls,
		points: "List[Point]"
	) -> "Point":
		"""
		"""
		return max(points, key = lambda point: point.lat)
	
	@classmethod
	def furthest_south(
		cls,
		points: "List[Point]"
	) -> "Point":
		"""
		"""
		return min(points, key = lambda point: point.lat)
	
	@classmethod
	def furthest_east(
		cls,
		points: "List[Point]"
	) -> "Point":
		"""
		"""
		return max(points, key = lambda point: point.lon)
	
	@classmethod
	def furthest_west(
		cls,
		points: "List[Point]"
	) -> "Point":
		"""
		"""
		return min(points, key = lambda point: point.lon)
	
	@classmethod
	def get_slope(
		cls, 
		p1: "Point",
		p2: "Point"
	) -> float:
		"""
		Change in latitude over change in longitude

		Returns m for (lat) = m(lon). This is probably only
		good for short distances. Assumes p1 is the origin.
		"""
		return (p1.lat - p2.lat) / (p1.lon - p2.lon)
	
	@classmethod
	def interp_lat(
		cls,
		line_p1: "Point",
		line_p2: "Point",
		lon: float
	) -> float:
		"""
		"""
		slope = cls.get_slope(line_p1, line_p2)

		return line_p1.lat + (slope * (lon - line_p1.lon))
	
	@classmethod
	def interp_lon(
		cls,
		line_p1: "Point",
		line_p2: "Point",
		lat: float
	) -> float:
		slope = cls.get_slope(line_p1, line_p2)

		return line_p1.lon + ((1./slope) * (lat - line_p1.lat))
	
	def is_east_of_line(
		self,
		line_p1: "Point",
		line_p2: "Point"
	) -> bool:
		"""
		"""
		if line_p1.lon == line_p2.lon:
			return self.is_east_of(line_p1)

		line_point = Point((
			self.lat,
			self.interp_lon(line_p1, line_p2, self.lat)
		))

		return self.is_east_of(line_point)
	
	def is_west_of_line(
		self,
		line_p1: "Point",
		line_p2: "Point"
	) -> bool:
		"""
		"""
		if line_p1.lon == line_p2.lon:
			return self.is_west_of(line_p1)
		
		line_point = Point((
			self.lat,
			self.interp_lon(line_p1, line_p2, self.lat)
		))

		return self.is_west_of(line_point)
	
	def is_north_of_line(
		self,
		line_p1: "Point",
		line_p2: "Point"
	) -> bool:
		"""
		"""
		if line_p1.lat == line_p2.lat:
			return self.is_north_of(line_p1)
		
		line_point = Point((
			self.interp_lat(line_p1, line_p2, self.lon),
			self.lon
		))

		return self.is_north_of(line_point)
	
	def is_south_of_line(
		self,
		line_p1: "Point",
		line_p2: "Point"
	) -> bool:
		"""
		"""
		if line_p1.lat == line_p2.lat:
			return self.is_south_of(line_p1)
		
		line_point = Point((
			self.interp_lat(line_p1, line_p2, self.lon),
			self.lon
		))

		return self.is_south_of(line_point)

	
	@property
	def tuple(self) -> Tuple[float, float]: return (self._lat, self._lon)

	@property
	def lat(self) -> float: return self._lat

	@property
	def lon(self) -> float: return self._lon


def append_to_dict_of_lists(
	d: Dict[Any, List[Any]],
	key: Any,
	new_val: Any
) -> None:
	"""
	"""
	try:
		d[key].append(new_val)
	except KeyError:
		d[key] = [new_val]

def insert_in_dict_of_dicts(
	d: Dict[Any, Dict[Any, Any]],
	outer_key: Any,
	inner_key: Any,
	new_val: Any,
	mirror = False
) -> None:
	"""
	"""
	try:
		d[outer_key][inner_key] = new_val
	except KeyError:
		d[outer_key] = {}
		d[outer_key][inner_key] = new_val

	if mirror:
		try:
			d[inner_key][outer_key] = new_val
		except KeyError:
			d[inner_key] = {}
			d[inner_key][outer_key] = new_val

class RouteStyle:
	"""
	raw_nxt_rte_id = self._segment_edge.nxt_node.trip.route_id
	nxt_rte_id = self._s.mask_route(raw_nxt_rte_id)
	nxt_rte_id_prefix = self._s.get_route_id_prefix(raw_nxt_rte_id)
	nxt_rte_id_prefix_cap = nxt_rte_id_prefix[0].upper()+nxt_rte_id_prefix[1:]
	"""
	_raw_rte_id: str
	_s: Settings

	def __init__(
		self,
		raw_route_id: str,
		settings: Settings
	) -> None:
		"""
		"""
		self._raw_rte_id = raw_route_id
		self._s = settings

	@property
	def prefixed_route_name(self) -> str:
		return (
			f"{self._s.get_route_id_prefix(self._raw_rte_id)} "
			f"{self._s.mask_route(self._raw_rte_id)}"
		)
	
	@property
	def capital_prefixed_route_name(self) -> str:
		rn = self.prefixed_route_name
		return rn[0].upper() + rn[1:]
	
	@property
	def route_name(self) -> str:
		return self._s.mask_route(self._raw_rte_id)
	

class RightLeftEnum(Enum):
	RIGHT = 1
	LEFT = 2