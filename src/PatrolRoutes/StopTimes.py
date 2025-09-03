"""
Manage stop_times. Query by trip_id and stop_id
"""

from dataclasses import dataclass
import pandas as pd
from pathlib import Path
from typing import cast, Dict, List, Optional, TypedDict
import warnings


from .GTFSTime import GTFSTime
from .Utils import append_to_dict_of_lists


@dataclass
class StopTime:
	_trip_id: int
	_arr_time: GTFSTime
	_dep_time: Optional[GTFSTime]
	_stop_id: int
	_stop_seq: int
	_timepoint: bool

	@property
	def trip_id(self) -> int: return self._trip_id
	@property
	def arrival_time(self) -> GTFSTime: return self._arr_time
	@property
	def departure_time(self) -> GTFSTime: 
		if self._dep_time is None:
			return self._arr_time
		return self._dep_time
	@property
	def stop_id(self) -> int: return self._stop_id
	@property
	def stop_sequence(self) -> int: return self._stop_seq
	@property
	def is_timepoint(self) -> bool: return self._timepoint

	#def get_nx_node_name(self) -> str:
	#	return f"{self.trip_id}_{self.stop_id}"

	@property
	def name(self) -> str: return f"{self.trip_id}_{self.stop_id}_{self.stop_sequence}"


class StopTimes:
	## {stop_id: [stop_times]}
	_stop_id_d: Dict[int, List[StopTime]]

	## {trip_id: [stop_times]}
	_trip_id_d: Dict[int, List[StopTime]]

	class _StopTimeRow(TypedDict):
		"""
		Types are as they will be parsed by pandas
		"""
		trip_id: int
		arrival_time: str
		departure_time: str
		stop_id: int
		stop_sequence: int
		stop_headsign: str
		pickup_type: int
		drop_off_type: int
		shape_dist_traveled: float
		timepoint: int

	def __init__(
		self,
		stoptime_path: Path
	) -> None:
		"""
		"""
		self._stop_id_d = {}
		self._trip_id_d = {}

		with warnings.catch_warnings():
			warnings.filterwarnings("ignore")

			stoptimes_df = pd.read_csv(stoptime_path)

		for _, row in stoptimes_df.iterrows():
			stoptime_row = cast("StopTimes._StopTimeRow", row)

			arr_time = GTFSTime(stoptime_row["arrival_time"])
			dep_time = GTFSTime(stoptime_row["departure_time"])

			if arr_time == dep_time:
				dep_time = None

			new_stoptime = StopTime(
				stoptime_row["trip_id"],
				arr_time,
				dep_time,
				stoptime_row["stop_id"],
				stoptime_row["stop_sequence"],
				bool(stoptime_row["timepoint"])
			)

			append_to_dict_of_lists(
				self._stop_id_d,
				new_stoptime.stop_id,
				new_stoptime
			)

			append_to_dict_of_lists(
				self._trip_id_d,
				new_stoptime.trip_id,
				new_stoptime
			)

		for stop_id in self._stop_id_d.keys():
			self._stop_id_d[stop_id] = sorted(
				self._stop_id_d[stop_id],
				key = lambda x: x.departure_time
			)

		for trip_id in self._trip_id_d.keys():
			self._trip_id_d[trip_id] = sorted(
				self._trip_id_d[trip_id],
				key = lambda x: x.departure_time
			)
	
	def get_stop_stoptimes(
		self,
		stop_id: int
	) -> List[StopTime]:
		"""
		Returns sorted stop_times from first to last stop.
		"""
		return self._stop_id_d[stop_id]
	
	def get_trip_stoptimes(
		self,
		trip_id: int
	) -> List[StopTime]:
		"""
		Returns sorted stop_times from first to last stop.
		"""
		return self._trip_id_d[trip_id]
	
	@classmethod
	def get_trip_id_set_from_stoptimes(
		cls,
		stoptimes: List[StopTime]
	) -> List[int]:
		"""
		"""
		trip_id_d = {}

		for stoptime in stoptimes:
			trip_id_d[stoptime.trip_id] = 1

		return list(trip_id_d.keys())




