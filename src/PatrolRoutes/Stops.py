"""
Location of all stops
"""


from dataclasses import dataclass
import pandas as pd
from pathlib import Path
from typing import cast, Dict, Iterator, List, TypedDict


from .StopTimes import StopTimes, StopTime
from .Utils import Point


@dataclass
class Stop:
	_stop_id: int
	_stop_name: str
	_stop_point: Point
	_stop_times: List[StopTime]

	@property
	def stop_id(self) -> int: return self._stop_id
	@property
	def stop_name(self) -> str: return self._stop_name
	@property
	def stop_point(self) -> Point: return self._stop_point
	@property
	def stop_times(self) -> List[StopTime]: return self._stop_times

	@property
	def standard_stop_name(self) -> str:
		tokens = self.stop_name.split(' & ')

		if len(tokens) == 1:
			return self.stop_name
		
		return ' & '.join(sorted(tokens))

	def __eq__(
		self,
		other: object
	) -> bool:
		if not isinstance(other, "Stop"):
			return False
		return self._stop_id == other.stop_id
	
	def _conv_to_tc(
		self,
		sname: str
	) -> str:
		"""
		"""
		tokens = sname.split()
		
		if tokens[-1] == "Station":
			tokens[-1] = "Transit Center"

		return ' '.join(tokens)
	
	@classmethod
	def same_standard_stop_names(
		cls,
		stop1: "Stop",
		stop2: "Stop"
	) -> bool:
		"""
		"""
		s1name = stop1._conv_to_tc(stop1.standard_stop_name)
		s2name = stop2._conv_to_tc(stop2.standard_stop_name)

		return stop1.standard_stop_name == stop2.standard_stop_name
	

class Stops:
	_stop_d: Dict[int, Stop]
	
	class _StopRow(TypedDict):
		stop_id: str
		stop_code: str
		stop_name: str
		stop_desc: str
		stop_lat: float
		stop_lon: float
		zone_id: str
		stop_url: str
		location_type: str
		parent_station: str
		wheelchair_boarding: int
		intersection_code: str
		reference_place: str
		stop_name_short: str
		stop_place: str

	def __init__(
		self,
		stops_path: Path,
		stop_times: StopTimes,
		skip_str_stops: bool = True
	) -> None:
		"""
		If `skip_str_stops` is `True`, skip stops whose IDs aren't integers.
		This might be an MTS-specific hack, likely not to generalize well
		to other agency feeds. 
		"""
		self._stop_d = {}

		stops_df = pd.read_csv(stops_path)

		for _, row in stops_df.iterrows():
			stop_row = cast("Stops._StopRow", row)

			if skip_str_stops:
				try:
					stop_id = int(stop_row["stop_id"])
				except ValueError:
					continue
			else:
				stop_id = stop_row["stop_id"]

			try:
				stop_stoptimes = stop_times.get_stop_stoptimes(int(stop_id))
			except KeyError:
				stop_stoptimes = []

			new_stop = Stop(
				int(stop_id),
				stop_row["stop_name"],
				Point((stop_row["stop_lat"], stop_row["stop_lon"])),
				stop_stoptimes
			)

			self._stop_d[new_stop.stop_id] = new_stop

	def __getitem__(
		self,
		stop_id: int
	) -> Stop:
		"""
		"""
		return self._stop_d[stop_id]
	
	def __iter__(self) -> Iterator[Stop]:
		"""
		"""
		for stop in self._stop_d.values():
			yield stop