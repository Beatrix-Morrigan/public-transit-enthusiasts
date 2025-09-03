"""
GTFS schema (future: will be actual in-memory relational database with 
sqlalchemy interface for likely faster access). 

		  Stops--GTFS--ServiceDates
			|	  |
			|	Trips 
			|	  |
			|---StopTimes

Objects can have pointers to each other not strictly in line 
with this hierarchy. This hiearchy defines the place
where actual objects are stored. 
"""


from datetime import datetime
from pathlib import Path
from typing import Iterator, List


from .GTFSService import DateServices
from .Trips import Trips, Trip
from .Settings import Settings
from .Shapes import Shapes
from .Stops import Stops, Stop
from .StopTimes import StopTimes, StopTime


class GTFS:
	"""
	Container + parser for all of the above. Route is top level, has trips,
	which have a shape and two or more stops. 
	"""
	_gtfs_strf: str = "%Y%m%d"

	_gtfs_dir: Path
	_services: DateServices
	_trips: Trips
	_stops: Stops
	_stop_times: StopTimes
	_shapes: Shapes

	def __init__(
		self,
		gtfs_dir: Path,
		settings: Settings
	) -> None:
		"""
		"""
		self._gtfs_dir = gtfs_dir

		print(f"Loading GTFS set at {self._gtfs_dir}...")

		print("\tLoading service info...")
		self._services = DateServices(
			self._gtfs_dir / "calendar.txt",
			self._gtfs_dir / "calendar_dates.txt"
		)

		print("\tLoading stop times...")
		self._stop_times = StopTimes(self._gtfs_dir / "stop_times.txt")

		print("\tLoading stops...")
		self._stops = Stops(
			self._gtfs_dir / "stops.txt",
			self._stop_times
		)

		print("\tLoading shapes...")
		self._shapes = Shapes(
			self._gtfs_dir / "shapes.txt"
		)

		print("\tLoading trips...")
		self._trips = Trips(
			self._gtfs_dir / "trips.txt",
			settings,
			self._stop_times,
			self._shapes
		)

		## TODO: Need to rewrite this entire codebase around a SQLAlchemy 
		## or similar in-memory relational database interface to
		## get rid of this line, should not exist.

		## Also not actually using this, trip can maybe add stops to shapes, not sure

		#print("\tAdding stops to shapes...")
		#self._shapes.add_stops(
		#	self._stops,
		#	self._trips
		#)

		print("done")
	
	def __repr__(self) -> str:
		return f"GTFS(gtfs_dir={self._gtfs_dir})"
	
	def get_date_trips(
		self,
		service_date: datetime
	) -> List[Trip]:
		"""
		"""
		date_service_ids = self._services.get_date_service_ids(service_date)

		ret_trips: List[Trip] = []

		for service_id in date_service_ids:
			try:
				ret_trips += self._trips.get_service_trips(service_id)
			except KeyError:
				continue

		return ret_trips

	def get_trip(
		self,
		trip_id: int
	) -> Trip:
		"""
		"""
		return self._trips[trip_id]
	
	def get_stop(
		self,
		stop_id: int
	) -> Stop:
		"""
		"""
		return self._stops[stop_id]
	
	def get_stop_stoptimes_on_date(
		self,
		service_date: datetime,
		stop_id: int
	) -> List[StopTime]:
		"""
		"""
		trips_on_date_d = {
			trip.trip_id: trip
			for trip in self.get_date_trips(service_date)
		}

		all_stop_stoptimes = self._stop_times.get_stop_stoptimes(stop_id)

		ret_stop_stoptimes: List[StopTime] = []

		for stop_time in all_stop_stoptimes:
			try:
				trips_on_date_d[stop_time.trip_id]
				ret_stop_stoptimes.append(stop_time)
			except KeyError:
				continue

		return ret_stop_stoptimes
	
	@property
	def stops(self) -> Stops:
		return self._stops




