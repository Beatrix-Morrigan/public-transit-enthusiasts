"""
Universal configuration object. Time/geographic constraints, route name masking,
route exclusions, etc.
"""


from datetime import datetime
import json
from pathlib import Path
from typing import cast, Dict, List, Optional, TypedDict


from . import GTFS_STRF
from .Duration import Minutes, Hours


class _SegmentGraphSettings(TypedDict):
	max_transfer_time_minutes: float
	min_transfer_time_minutes: float
	max_transfer_distance_miles: float
	transfer_timepoint_only: bool


class _LoopSettings(TypedDict):
	loop_max_duration_hours: float
	loop_min_duration_hours: float
	loop_min_segments: int
	trip_min_duration_minutes: float
	allow_consecutive_same_route: bool


class SettingsJSON(TypedDict):
	"""
	Types as expected to get directly from user input JSON. `Settings` class
	will manage returning expected types (`Minutes`, etc.). '_' fields are added
	immediately after loading, usually for faster lookup.
	"""
	gtfs_path: str
	walking_transfers_path: Optional[str]
	boundary_path: Optional[str]
	segment_graph_path: Optional[str]
	loops_path: None

	service_date: str

	route_id_masks: Dict[str, str]

	the_routes: List[str]
	_the_routes_d: Dict[str, bool]

	exclude_routes: List[str]
	_exclude_routes_d: Dict[str, bool]

	segment_graph: _SegmentGraphSettings
	loop: _LoopSettings


class Settings:
	_sd: SettingsJSON

	def __init__(
		self,
		path: Path
	) -> None:
		"""
		"""
		with open(path, 'r') as f:
			self._sd = cast(SettingsJSON, json.load(f))

		self._sd["_exclude_routes_d"] = {}
		for route_id in self._sd["exclude_routes"]:
			self._sd["_exclude_routes_d"][route_id] = True

		self._sd["_the_routes_d"] = {}
		for route_id in self._sd["the_routes"]:
			self._sd["_the_routes_d"][route_id] = True

	def _get_optional_path(
		self,
		path_str: Optional[str]
	) -> Optional[Path]:
		"""
		"""
		if path_str is None:
			return 
		return Path(path_str)
	
	## Masks + exclusions (not properties)
	def route_is_excluded(
		self,
		route_id: str
	) -> bool:
		"""
		"""
		try: 
			return self._sd["_exclude_routes_d"][route_id]
		except KeyError:
			return False
		
	def get_route_id_prefix(
		self,
		route_id: str
	) -> str:
		"""
		"""
		try:
			self._sd["_the_routes_d"][route_id]
			return "the"
		except KeyError:
			return "route"
		
	def mask_route(
		self,
		route_id: str
	) -> str:
		"""
		"""
		try:
			return self._sd["route_id_masks"][route_id]
		except KeyError:
			return route_id

	## Segment Graph options

	@property
	def max_transfer_time(self) -> Minutes: 
		return Minutes(self._sd["segment_graph"]["max_transfer_time_minutes"])
	
	@property
	def min_transfer_time(self) -> Minutes:
		return Minutes(self._sd["segment_graph"]["min_transfer_time_minutes"])
	
	@property
	def max_transfer_distance(self) -> float:
		return self._sd["segment_graph"]["max_transfer_distance_miles"]
	
	@property
	def transfer_timepoint_only(self) -> bool:
		return self._sd["segment_graph"]["transfer_timepoint_only"]
	
	## Loop options
	
	@property
	def loop_max_duration(self) -> Hours:
		return Hours(self._sd["loop"]["loop_max_duration_hours"])
	
	@property
	def loop_min_duration(self) -> Hours:
		return Hours(self._sd["loop"]["loop_min_duration_hours"])
	
	@property
	def loop_min_segments(self) -> int:
		return self._sd["loop"]["loop_min_segments"]
	
	@property
	def trip_min_duration(self) -> Minutes:
		return Minutes(self._sd["loop"]["trip_min_duration_minutes"])
	
	@property
	def allow_consecutive_same_route(self) -> bool:
		return self._sd["loop"]["allow_consecutive_same_route"]
	
	## Misc options
	
	@property
	def gtfs_path(self) -> Path:
		return Path(self._sd["gtfs_path"])
	
	@property
	def walking_transfers_path(self) -> Optional[Path]:
		return self._get_optional_path(self._sd["walking_transfers_path"])
	
	@property
	def boundary_path(self) -> Optional[Path]:
		return self._get_optional_path(self._sd["boundary_path"])
	
	@property
	def segment_graph_path(self) -> Optional[Path]:
		seg_path = self._sd["segment_graph_path"]

		if seg_path is None:
			return None
		
		return Path(seg_path)
	
	@property
	def loops_path(self) -> Optional[Path]:
		raise NotImplementedError
	
	@property
	def service_date(self) -> datetime:
		return datetime.strptime(
			self._sd["service_date"],
			GTFS_STRF
		)