"""
Points of interest.

How to do this:

=============

Can give TripEdge a list of ShapeSegments depending on begining/end starttimes 
- Shape needs query function to get list of segments between two stops for a trip

Populating:
-----------
- Find a representative trip
- Add all stops from trip to specific ShapeSegment
- Check all POIs if associated with a stop, add them
	- POIs should be small number and these shoudl all be dict queries

Shapes
  |- {shape_id: Shape}
				  |- {stop_id: ShapeSegment}
				  |- {poi_id: ShapeSegment}
				  |- [ShapeSegment]
				  		|- {stop_id: Stop}
						|- {poi_id: POI}
						|- .get_poi_instructions()

Querying:
---------
	TripEdge.get_pois(); then filter them for in range or not
		|
	Trip.get_pois()
		|
	Shape.get_pois()
		|
	ShapeSegment.get_pois() for all segments in Shape
"""


from pathlib import Path
from typing import Dict, Iterator, List, Optional, TypedDict


from .Utils import Point


class POIJSON(TypedDict):
	name: str
	type: str
	lat: float
	lon: float
	stop_ids: List[str]
	notes: Optional[str]


class POI:
	_poi_rec: POIJSON

	def __init__(
		self,
		poi_rec: POIJSON
	) -> None:
		"""
		"""
		self._poi_rec = poi_rec

	
	def __str__(self) -> str:
		"""
		"""
		ret_s = f"{self.name} ({self.type})"
		if self.notes is not None:
			ret_s += f" - {self.notes}"
		return ret_s
	
	## Properties

	@property
	def name(self) -> str: return self._poi_rec["name"]
	@property
	def type(self) -> str: return self._poi_rec["type"]
	@property
	def lat(self) -> float: return self._poi_rec["lat"]
	@property
	def lon(self) -> float: return self._poi_rec["lon"]
	@property
	def point(self) -> Point: return Point((self.lat, self.lon))
	@property
	def stop_ids(self) -> List[str]: return self._poi_rec["stop_ids"]
	@property
	def notes(self) -> str:
		notes = self._poi_rec["notes"]
		if notes is None:
			return ""
		if notes[-1] != '.':
			return notes +'.'
		return notes

	
class POIs:
	_pois: List[POI]
	_stop_poi_d: Dict[str, POI] ## mapping of stop IDs to POIs

	def __init__(
		self,
		recs: List[POIJSON]
	) -> None:
		"""
		"""
		raise NotImplementedError
	
	def __getitem__(
		self,
		stop_id: str
	) -> List[POI]:
		"""
		"""
		raise NotImplementedError
	
	def __iter__(
		self,
	) -> Iterator[POI]:
		"""
		"""
		raise NotImplementedError
	
	@classmethod
	def from_pois_json(
		cls,
		path: Path
	) -> "POIs":
		"""
		"""
		raise NotImplementedError