"""
Represents trips, query by ID (int) or service_id (str).
"""


from dataclasses import dataclass
import pandas as pd
from pandas._libs.missing import NAType
from pathlib import Path
from typing import cast, Dict, List, TypedDict


from .Settings import Settings
from .Shapes import Shapes, Shape, UnknownShapeException
from .StopTimes import StopTimes, StopTime
from .Utils import append_to_dict_of_lists


class NullTripShapeException(Exception):
	def __init__(
		self,
		trip_row: "_TripRow"
	) -> None:
		"""
		"""
		super().__init__((
			f"Trip {trip_row['trip_id']} on route {trip_row['route_id']} "
			f"has no associated shape. Route {trip_row['route_id']} may need "
			f"to be added to 'exclude_routes' in settings JSON."
		))


@dataclass
class Trip:
	_route_id: str
	_service_id: str
	_trip_id: int
	_trip_headsign: str
	_stop_times: List[StopTime]
	_direction_name: str
	_shape: Shape

	@property
	def route_id(self) -> str: return self._route_id
	@property
	def service_id(self) -> str: return self._service_id
	@property
	def trip_id(self) -> int: return self._trip_id
	@property
	def trip_headsign(self) -> str: return self._trip_headsign
	@property
	def stop_times(self) -> List[StopTime]: return self._stop_times
	@property
	def direction_name(self) -> str: return self._direction_name
	@property
	def shape(self) -> Shape: return self._shape

	@property
	def first_stoptime(self) -> StopTime: return self._stop_times[0]
	@property
	def last_stoptime(self) -> StopTime: return self._stop_times[-1]


class _TripRow(TypedDict):
	"""
	Types are as pandas will parse them.
	"""
	route_id: str
	service_id: str
	trip_id: int
	trip_headsign: str
	direction_id: int
	block_id: int
	shape_id: str|NAType
	wheelchair_accessible: int
	bikes_allowed: int
	direction_name: str
	trip_bikes_allowed: int
	trip_headsign_short: str


class Trips:
	"""
	All of the trips stored by trip_id and service_id
	"""

	_trip_d: Dict[int, Trip]
	_svc_trips_d: Dict[str, List["Trip"]]
		
	def __init__(
		self,
		trips_path: Path,
		settings: Settings,
		stop_times: StopTimes,
		shapes: Shapes
	) -> None:
		"""
		"""
		self._trip_d = {}
		self._svc_trips_d = {}

		trips_df = pd.read_csv(trips_path)

		for _, row in trips_df.iterrows():
			trip_row = cast("_TripRow", row.to_dict())

			if settings.route_is_excluded(trip_row['route_id']):
				continue

			if pd.isnull(trip_row['shape_id']):
				raise NullTripShapeException(trip_row)
			else:  ## type hinting
				trip_row['shape_id'] = cast(str, trip_row['shape_id'])

			new_trip = Trip(
				trip_row["route_id"],
				trip_row["service_id"],
				trip_row["trip_id"],
				trip_row["trip_headsign"],
				stop_times.get_trip_stoptimes(trip_row["trip_id"]),
				trip_row["direction_name"],
				shapes[trip_row['shape_id']]
			)

			self._trip_d[new_trip.trip_id] = new_trip

			append_to_dict_of_lists(
				self._svc_trips_d,
				new_trip.service_id,
				new_trip
			)
	
	def __getitem__(
		self,
		trip_id: int
	) -> Trip:
		"""
		"""
		return self._trip_d[trip_id]
	
	def get_service_trips(
		self,
		service_id: str
	) -> List[Trip]:
		"""
		"""
		try:
			return self._svc_trips_d[service_id]
		except KeyError:
			raise KeyError(
				f"The service '{service_id}' has no associated trips."
			)