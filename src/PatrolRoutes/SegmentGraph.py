"""
Represent possible transit paths as connections of route/time segments
and transfer points when physically/temporally possible. Transfer points
are a stop with more than one route or two stops with one or more
differing routes that are less than some configurable distances apart.
"""


from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import networkx as nx
import numpy as np
from pathlib import Path
import pickle
from typing import List, Dict, Generic, Optional, overload, Type, TypeVar
import warnings


from .Duration import BaseDuration, Hours, Minutes, Seconds
from .GTFS import GTFS
from .GTFSTime import GTFSTime
from .PolygonBoundary import PolygonBoundary
from .Stops import Stop
from .Trips import Trip
from .Settings import Settings
from .StopTimes import StopTimes, StopTime
from .Utils import Point, append_to_dict_of_lists, insert_in_dict_of_dicts


@dataclass
class Boundary:
	_northwest: Point
	_northeast: Point
	_southeast: Point
	_southwest: Point

	@property
	def northwest(self) -> Point: return self._northwest
	@property
	def northeast(self) -> Point: return self._northeast
	@property
	def southeast(self) -> Point: return self._southeast
	@property
	def southwest(self) -> Point: return self._southwest

	def __eq__(
		self,
		other: object
	) -> bool:
		if not isinstance(other, Boundary):
			return False
		return (
				self.northwest == other.northwest
			and self.northeast == other.northeast
			and self.southwest == other.southwest
			and self.southeast == other.southeast
		)
	
	def __str__(self) -> str:
		return (
			f"Boundary(northwest={self.northwest}, "
			f"northeast={self.northeast}, "
			f"southeast={self.southeast}, "
			f"southwest={self.southwest})"
		)

	def contains(
		self,
		point: Point
	) -> bool:
		return (
				point.is_east_of_line(self.southwest, self.northwest)
			and point.is_west_of_line(self.southeast, self.northeast)
			and point.is_north_of_line(self.southwest, self.southeast)
			and point.is_south_of_line(self.northwest, self.northeast)
		)
	

class WalkingTransfers:
	_wt_d: Dict[int, Dict[int, float]]
	_boundary: Optional[PolygonBoundary]
	_max_dist: float

	def __init__(
		self,
		stops: List[Stop],
		boundary: Optional[PolygonBoundary],
		max_dist: float
	) -> None:
		"""
		"""
		self._wt_d = {}
		self._boundary = boundary
		self._max_dist = max_dist

		n_walking_transfers = 0
		n_waiting_tranfsers = 0
		nz_dists = []

		n_stops = len(stops)
		print(f"Checking walking transfers for {n_stops} stops...")

		for i, stop1 in enumerate(stops):
			if i % 100 == 0:
				print(f"Have checked {((float(i)/n_stops)*100):.2f}% of stops...")

			for stop2 in stops:

				if stop1 is stop2:
					insert_in_dict_of_dicts(
						self._wt_d,
						stop1.stop_id,
						stop2.stop_id,
						0.0,
						mirror = True
					)
					n_waiting_tranfsers += 1

				try:
					self._wt_d[stop2.stop_id][stop1.stop_id]
					continue
				except KeyError:
					dist = stop1.stop_point.distance_to(stop2.stop_point)

					nz_dists.append(dist)

					insert_in_dict_of_dicts(
						self._wt_d,
						stop1.stop_id,
						stop2.stop_id,
						dist,
						mirror = True
					)

					n_walking_transfers += 1
	
	@classmethod
	def load(
		cls,
		path: str,
		curr_boundary: PolygonBoundary
	) -> "WalkingTransfers":
		"""
		"""
		with open(str(Path(path)), 'rb') as f:
			wt: "WalkingTransfers" = pickle.load(f)
			
		if wt._boundary != curr_boundary:
			warnings.warn((
				f"Geographic boundary provided ({curr_boundary}) does not "
				f"match boundary in loaded WalkingTransfers ({wt._boundary})."
			))
		
		return wt
	
	def save(
		self,
		path: str
	) -> None:
		"""
		"""
		with open(str(Path(path)), 'wb') as f:
			pickle.dump(self, f)
	
	def get_transfer(
		self,
		stop1: Stop,
		stop2: Stop
	) -> Optional[float]:
		"""
		"""
		try:
			return self._wt_d[stop1.stop_id][stop2.stop_id]
		except KeyError:
			return None
			
			
## New version below, stop using NX

class StopTimeNode:
	_stoptime: StopTime
	_trip: Trip
	_stop: Stop
	_prv_edges: "Dict[str, Edge]"
	_nxt_edges: "Dict[str, Edge]"

	def __init__(
		self,
		gtfs: GTFS,
		stoptime: StopTime
	) -> None:
		"""
		"""
		self._stoptime = stoptime
		self._trip = gtfs.get_trip(stoptime.trip_id)
		self._stop = gtfs.get_stop(stoptime.stop_id)
		self._prv_edges = {}
		self._nxt_edges = {}

	def __str__(self) -> str:
		return self._stoptime.name

	def get_random_next_edge(
		self,
		rng: np.random.Generator
	) -> "Edge":
		"""
		"""
		nxt_edges_l = list(self._nxt_edges.values())
		nxt_edge_indx = int(rng.choice(
			len(nxt_edges_l),
			size = 1
		))
		return nxt_edges_l[nxt_edge_indx]
	
	def get_shuffled_next_edges(
		self,
		rng: np.random.Generator
	) -> "List[Edge]":
		"""
		"""
		nxt_edges = np.asarray(list(self._nxt_edges.values()))

		rng.shuffle(nxt_edges)

		return nxt_edges.tolist()

	@property
	def arrival_time(self) -> GTFSTime: return self._stoptime.arrival_time

	@property
	def departure_time(self) -> GTFSTime: return self._stoptime.departure_time

	@property
	def trip(self) -> Trip: return self._trip

	@property
	def stop(self) -> Stop: return self._stop

	@property
	def stoptime(self) -> StopTime: return self._stoptime

	@property
	def stop_sequence(self) -> int: return self._stoptime.stop_sequence

	@property
	def is_timepoint(self) -> bool: return self._stoptime.is_timepoint

	@property
	def name(self) -> str: 
		return self._stoptime.name

	@property
	def prv_edges(self) -> "Dict[str, Edge]":
		return self._prv_edges
	
	def add_prv_edge(
		self,
		edge: "Edge"
	) -> None:
		"""
		"""
		self._prv_edges[edge.name] = edge
	
	@property
	def nxt_edges(self) -> "Dict[str, Edge]":
		return self._nxt_edges
	
	def add_nxt_edge(
		self,
		edge: "Edge"
	) -> None:
		"""
		"""
		self._nxt_edges[edge.name] = edge


class Edge(ABC):
	_prv_node: StopTimeNode
	_nxt_node: StopTimeNode
	_duration: BaseDuration

	@abstractmethod
	def __init__(
		self,
		prv_node: StopTimeNode,
		nxt_node: StopTimeNode,
	) -> None:
		pass

	@property
	@abstractmethod
	def prv_node(self) -> StopTimeNode:
		pass

	@property
	@abstractmethod
	def nxt_node(self) -> StopTimeNode:
		pass

	@property
	@abstractmethod
	def duration(self) -> BaseDuration:
		pass

	@property
	@abstractmethod
	def distance(self) -> float:
		pass

	@property
	@abstractmethod
	def name(self) -> str:
		pass


class TripEdge(Edge):
	_prv_node: StopTimeNode
	_nxt_node: StopTimeNode
	_duration: BaseDuration

	_distance: float ## interpret this as number of stops
	
	_trip: Trip

	def __init__(
		self,
		prv_node: StopTimeNode,
		nxt_node: StopTimeNode
	) -> None:
		"""
		"""
		if prv_node.trip.trip_id != nxt_node.trip.trip_id:
			raise ValueError(
				f"Can't connect stoptimes with different trips "
				f"'{prv_node.name}' and "
				f"'{nxt_node.name}'"
			)
		
		self._prv_node = prv_node
		self._nxt_node = nxt_node
		
		try:
			self._duration = (
				Seconds(self._nxt_node.departure_time - self._prv_node.arrival_time)
			)
		except GTFSTime.InvalidGTFSTimeException:
			raise ValueError(
				f"TripEdge from {self._prv_node.name} to {self._nxt_node.name} is "
				f"invalid because next departure {self._nxt_node.departure_time.to_fstr()} "
				f"is before previous arrival {self._prv_node.arrival_time.to_fstr()}."
			)

		self._distance = (
			nxt_node.stop_sequence - prv_node.stop_sequence
		)

		self._trip = prv_node.trip

	@property
	def prv_node(self) -> StopTimeNode: return self._prv_node

	@property
	def nxt_node(self) -> StopTimeNode: return self._nxt_node

	@property
	def duration(self) -> BaseDuration: return self._duration

	@property
	def distance(self) -> float: return self._distance

	@property
	def trip(self) -> Trip: return self._trip

	@property
	def name(self) -> str:
		return (
			f"trip-{self._trip.trip_id}_start-"
			f"{self.prv_node}_end-"
			f"{self.nxt_node}"
		)


class TransferEdge(Edge):
	_prv_node: StopTimeNode
	_nxt_node: StopTimeNode
	_duration: BaseDuration

	_distance: float

	def __init__(
		self,
		prv_node: StopTimeNode,
		nxt_node: StopTimeNode
	) -> None:
		"""
		"""
		self._prv_node = prv_node
		self._nxt_node = nxt_node

		self._duration = (
			Seconds(nxt_node.departure_time - prv_node.arrival_time)
		)

		self._distance = (
			prv_node.stop.stop_point.distance_to(nxt_node.stop.stop_point)
		)

	@property
	def prv_node(self) -> StopTimeNode: return self._prv_node
	
	@property
	def nxt_node(self) -> StopTimeNode: return self._nxt_node

	@property
	def duration(self) -> BaseDuration: return self._duration

	@property
	def distance(self) -> float: return self._distance

	@property
	def name(self) -> str:
		return (
			f"transfer_start-{self.prv_node.name}_end-{self.nxt_node.name}"
		)
	

class STJoinType(Enum):
	TRIP = 1
	TRANFSER = 2


class SegmentGraph:
	"""
	nodes are stoptime stops
		- so same physical stop can repeat many times
	edges are 
		- vehicle driving from stop to stop
		- walking/waiting transfer
	"""
	_gtfs_path: Path
	_service_date: datetime
	_max_time: Minutes
	_min_time: Minutes
	_max_dist: float
	_wt_path: Optional[Path]
	_boundary: Optional[PolygonBoundary]
	_only_tp: bool

	_gtfs: GTFS
	_wt: WalkingTransfers
	
	_stoptime_nodes: Dict[str, StopTimeNode]
	_edges: Dict[str, Edge]

	_s: Settings ## Save for any other reason needed like passing to other objs

	def __init__(
		self,
		settings: Settings
	) -> None:
		"""
		"""
		self._gtfs_path = settings.gtfs_path
		self._service_date = settings.service_date
		self._max_time = settings.max_transfer_time
		self._min_time = settings.min_transfer_time
		self._max_dist = settings.max_transfer_distance
		self._wt_path = settings.walking_transfers_path
		
		if settings.boundary_path is not None:
			self._boundary = PolygonBoundary(
				settings.boundary_path
			)
		else:
			self._boundary = None

		self._only_tp = settings.transfer_timepoint_only

		self._s = settings

		self._stoptime_nodes = {}
		self._edges = {}

	def _get_transfer(
		self,
		from_stoptime: StopTime,
		to_stoptime: StopTime
	) -> Optional[float]:
		"""
		"""
		## Enforce timepoint limit if set
		if self._only_tp and not (from_stoptime.is_timepoint and to_stoptime.is_timepoint):
			return None

		return self._wt.get_transfer(
			self._gtfs.get_stop(from_stoptime.stop_id),
			self._gtfs.get_stop(to_stoptime.stop_id)
		)
		
	def _get_time_grouped_stoptimes(
		self,
		use_stops: List[Stop]
	) -> Dict[GTFSTime, List[StopTime]]:
		"""
		Get lists of all stop_times with arrivals at each second
		"""
		t_d = {}

		for stop in use_stops:
			#for stop_time in stop.stop_times:
			try:
				for stop_time in self._gtfs.get_stop_stoptimes_on_date(self._service_date, stop.stop_id):
					append_to_dict_of_lists(
						t_d,
						stop_time.arrival_time,
						stop_time
					)
			except KeyError:
				continue

		return t_d
	
	def _stoptimes_compatible(
		self,
		st1: StopTimeNode,
		st2: StopTimeNode
	) -> Optional[STJoinType]:
		"""
		"""
		if self._only_tp and (not (st1._stoptime.is_timepoint and st2.is_timepoint)):
			return None

		if st1.trip.trip_id == st2.trip.trip_id:
			if st2.stop_sequence > st1.stop_sequence:
				return STJoinType.TRIP
			else:
				return None
			
		if self._wt.get_transfer(st1.stop, st2.stop) is None:
			return None
		elif Seconds(st2.departure_time - st1.arrival_time) > self._max_time:
			return None
		else:
			return STJoinType.TRANFSER
		
	def _add_edge(
		self,
		stname1: str,
		stname2: str,
		edge_type: STJoinType
	) -> None:
		"""
		"""
		stnode1 = self._stoptime_nodes[stname1]
		stnode2 = self._stoptime_nodes[stname2]

		if self._stoptimes_compatible(stnode1, stnode2) != edge_type:
			return

		if edge_type == STJoinType.TRANFSER:
			new_edge = TransferEdge(stnode1, stnode2)
		elif edge_type == STJoinType.TRIP:
			new_edge = TripEdge(stnode1, stnode2)
		else:
			raise ValueError(
				f"Got unexpected STJoinType {edge_type}."
			)
		
		self._edges[new_edge.name] = new_edge

		stnode1.add_nxt_edge(new_edge)
		stnode2.add_prv_edge(new_edge)

	def build_graph(
		self
	) -> None:
		"""
		"""
		## Load GTFS
		self._gtfs = GTFS(self._gtfs_path, self._s)

		## Filter to stops in boundary
		print("Building segment graph...")

		if self._boundary is not None:
			use_stops = [
				stop for stop in self._gtfs.stops
				if self._boundary.contains(stop.stop_point)
			]
		else:
			use_stops = [
				stop for stop in self._gtfs.stops
			]

		## load or build walking transfers
		if self._wt_path is not None:
			with open(self._wt_path, 'rb') as f:
				self._wt = pickle.load(f)
		else:
			self._wt = WalkingTransfers(
				use_stops,
				self._boundary,
				self._max_dist
			)

		## Get all stop times sorted by departure time
		st_all_d = self._get_time_grouped_stoptimes(use_stops)
		times_ordered = sorted(list(st_all_d.keys()))

		## Add nodes
		for gt in st_all_d.keys():
			for stoptime in st_all_d[gt]:
				try:
					self._stoptime_nodes[stoptime.name]
				except KeyError:
					self._stoptime_nodes[stoptime.name] = StopTimeNode(
						self._gtfs,
						stoptime
					)

		## Connect same trip stoptimes with TripEdge
		trip_ids = StopTimes.get_trip_id_set_from_stoptimes([
			node.stoptime for node in self._stoptime_nodes.values()
		])

		for trip_id in trip_ids:
			trip_st = self._gtfs.get_trip(trip_id).stop_times

			for st1 in trip_st:
				for st2 in trip_st:
					#if st1.stop_sequence >= st2.stop_sequence:
					#	continue
					#if self._only_tp and not (st1.is_timepoint and st2.is_timepoint):
					#	continue

					try:
						self._add_edge(st1.name, st2.name, STJoinType.TRIP)
					except KeyError:
						## Assuming this is for trips that extend outside boundary.
						## We will ignore them, it will be like trip ends at 
						## last valid stop before boundary.
						continue

		## Connect walking/waiting transfers with TransferEdge

		for _, arr_time_1 in enumerate(times_ordered):

			if int(arr_time_1)%3600 == 0:
				print(f"Checking arr_time_1 {arr_time_1.to_fstr()}")

			for from_st in st_all_d[arr_time_1]:
				offset = self._min_time

				while offset <= self._max_time:
					arr_time_2 = arr_time_1 + offset
					
					try:
						st_all_d[arr_time_2]
					except KeyError:
						offset += Minutes(1)
						continue

					for to_st in st_all_d[arr_time_2]:
						tdist = self._wt.get_transfer(
							self._gtfs.get_stop(from_st.stop_id),
							self._gtfs.get_stop(to_st.stop_id)
						)

						if (tdist is not None) and (tdist <= self._max_dist):
							self._add_edge(
								from_st.name,
								to_st.name,
								STJoinType.TRANFSER
							)

					offset += Minutes(1)


		#n_trip_edges = len([
		#	edge for edge in self._edges.values()
		#	if isinstance(edge, TripEdge)
		#])

		n_transfer_edges = len([
			edge for edge in self._edges.values()
			if isinstance(edge, TransferEdge)
		])

		print(f"Built graph with {len(self._stoptime_nodes)} stoptimes, {len(set(trip_ids))} trips, and {n_transfer_edges} transfers.")


	@property
	def edges(self) -> Dict[str, Edge]: return self._edges

	@property
	def edge_names(self) -> List[str]: return list(self._edges.keys())

	@property 
	def trip_edges(self) -> List[TripEdge]:
		return [
			edge for edge in self._edges.values()
			if isinstance(edge, TripEdge)
		]
	
	def save(
		self,
		path: Path
	) -> None:
		"""
		"""
		with open(path, 'wb') as f:
			pickle.dump(self, f)

	@classmethod
	def load(
		cls,
		path: Path
	) -> "SegmentGraph":
		"""
		"""
		with open(path, 'rb') as f:
			return pickle.load(f)
