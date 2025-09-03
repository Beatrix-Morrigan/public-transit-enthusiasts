"""
Data structures for the main route-finding algorithm in Loop.py
"""


from abc import ABC, abstractmethod, ABCMeta
from typing import Generic, List, Tuple, Type, TypeVar, Optional


from .Duration import BaseDuration, Minutes
from .GTFSTime import GTFSTime
#from .LinkedList import LLContainerNode, LLContainer
from .LinkedList import BaseLLNode, BaseLL
from .SegmentGraph import Edge as SegmentEdge
from .SegmentGraph import TripEdge as SegmentTripEdge
from .SegmentGraph import TransferEdge as SegmentTransferEdge
from .Settings import Settings
from .Stops import Stop
from .Utils import RouteStyle as RS


#O = Optional ## Going to be typing this a lot, no pun intended.


SEG_EDGE_T = TypeVar("SEG_EDGE_T", bound = SegmentEdge)
NXT_PRV_T = TypeVar("NXT_PRV_T", bound = "LoopNode") ## These are conveniently always the same type(s)
class LoopNode(BaseLLNode[NXT_PRV_T, NXT_PRV_T], ABC, Generic[NXT_PRV_T, SEG_EDGE_T]):
	_segment: SEG_EDGE_T
	_prv: Optional[NXT_PRV_T]
	_nxt: Optional[NXT_PRV_T]

	_loop_num: int
	_seg_num: int
	_s: Settings

	def __init__(
		self,
		loop_number: int,
		segment_number: int,
		segment: SEG_EDGE_T,
		settings: Settings
	) -> None:
		"""
		"""
		## initializes neighbors to None
		super().__init__()

		self._segment = segment
		self._loop_num = loop_number
		self._seg_num = segment_number
		self._s = settings

	@property
	def name(self) -> str: return self._segment.name

	@property
	def segment_number(self) -> int: return self._seg_num

	@property
	def from_stop(self) -> Stop: return self._segment.prv_node.stop

	@property
	def to_stop(self) -> Stop: return self._segment.nxt_node.stop

	@property
	def segment_edge(self) -> SEG_EDGE_T: return self._segment

	@property
	def from_departure_time(self) -> GTFSTime: 
		return self._segment.prv_node.departure_time
	
	@property
	def to_arrival_time(self) -> GTFSTime:
		return self._segment.nxt_node.arrival_time


class TripNode(LoopNode["WaitingNode|WalkingNode", SegmentTripEdge]):
	_segment: SegmentTripEdge
	_prv: "Optional[WaitingNode|WalkingNode]"
	_nxt: "Optional[WaitingNode|WalkingNode]"

	_loop_num: int
	_seg_num: int
	_s: Settings

	def __str__(self) -> str:
		"""
		"""
		from_dep_time = self.from_departure_time.to_fstr(use_ampm = True)

		rte = RS(self._segment.trip.route_id, self._s)

		hdsgn = self._segment.trip.trip_headsign

		dirname = self._segment.trip

		from_stop_name = self.from_stop.stop_name

		dist = self._segment.distance

		duration = Minutes(self._segment.duration)

		to_arr_time = self.to_arrival_time.to_fstr(use_ampm = True)

		to_stop_name = self.to_stop.stop_name

		return f"""STEP {self._seg_num} | {rte.prefixed_route_name} (to {hdsgn}) | {int(dist)} stops, {duration}
		----------------------------------------------
		{from_dep_time}: Board at {from_stop_name}.
		{to_arr_time}: Exit at {to_stop_name}.
		==============================================
		"""


class WaitingNode(LoopNode["TripNode", SegmentTransferEdge]):
	"""
	Use this when transfer is at the same stop.
	"""
	_segment: SegmentTransferEdge
	_prv: "Optional[TripNode]"
	_nxt: "Optional[TripNode]"

	_loop_num: int
	_seg_num: int
	_s: Settings

	def __str__(self) -> str:
		from_dep_time = self.from_departure_time.to_fstr(use_ampm = True)

		from_stop_name = self.from_stop.stop_name

		nxt_rte = RS(self._segment.nxt_node.trip.route_id, self._s)

		nxt_dirname = self._segment.nxt_node.trip.direction_name

		nxt_rte_hdsgn = self._segment.nxt_node.trip.trip_headsign

		to_arr_time = self.to_arrival_time.to_fstr(
			use_ampm = True
		)

		to_dep_time = self._segment.nxt_node.departure_time.to_fstr(
			use_ampm = True
		)

		ttime = (
			self._segment.nxt_node.departure_time
			- self._segment.prv_node.arrival_time
		)

		return f"""STEP {self._seg_num} | Wait here | {Minutes(ttime)} transfer
		----------------------------------------------
		{from_dep_time}: Wait here {nxt_rte.prefixed_route_name} (to {nxt_rte_hdsgn}).
		{to_dep_time}: {nxt_rte.capital_prefixed_route_name} (to {nxt_rte_hdsgn}) scheduled departure.
		==============================================
		"""


class WalkingNode(LoopNode["TripNode", SegmentTransferEdge]):
	"""
	Use this when transfer is between different stops.
	"""
	_segment: SegmentTransferEdge
	_prv: "Optional[TripNode]"
	_nxt: "Optional[TripNode]"

	_loop_num: int
	_seg_num: int
	_s: Settings

	def __str__(self) -> str:
		from_dep_time = self.from_departure_time.to_fstr(
			use_ampm = True
		)

		#print(self.from_stop.stop_name, self.to_stop.stop_name)
		#print(self.from_stop.standard_stop_name, self.to_stop.standard_stop_name)

		same_tc_intersection = Stop.same_standard_stop_names(self.from_stop, self.to_stop)

		if same_tc_intersection:
			walk_inst = f"Walk to the stop for"
		else:
			walk_inst = f"Walk to {self.to_stop.stop_name} for"

		nxt_rte = RS(self._segment.nxt_node.trip.route_id, self._s)

		nxt_dirname = self._segment.nxt_node.trip.direction_name

		distance = self._segment.distance

		ttime = (
			self._segment.nxt_node.departure_time
			- self._segment.prv_node.arrival_time
		)

		to_arr_time = self.to_arrival_time.to_fstr(use_ampm = True)

		to_dep_time = self._segment.nxt_node.departure_time.to_fstr(
			use_ampm = True
		)

		nxt_rte_hdsgn = self._segment.nxt_node.trip.trip_headsign

		if same_tc_intersection:
			inst_header = f"Walk to {nxt_rte.prefixed_route_name} (to {nxt_rte_hdsgn}) in {Minutes(ttime)}"
		else:
			inst_header = f"Walk to {self.to_stop.stop_name} for (to {nxt_rte_hdsgn}) in {Minutes(ttime)}"

		return f"""STEP {self._seg_num} | {inst_header} | {Minutes(ttime)} transfer
		----------------------------------------------
		{from_dep_time}: {walk_inst} {nxt_rte.prefixed_route_name} to {nxt_rte_hdsgn}.
				{distance:0.2f} miles, {Minutes(ttime)} to transfer
		{to_arr_time}: {nxt_rte.capital_prefixed_route_name} (to {nxt_rte_hdsgn}) scheduled to arrive.
		==============================================
		"""


class LoopLL(BaseLL[LoopNode]):
	_root: Optional[LoopNode[WalkingNode|WaitingNode, SegmentTripEdge]]
	_inc: List[Tuple[Type[LoopNode], Type[LoopNode]]]

	def __init__(
		self
	) -> None:
		"""
		"""
		super().__init__([
			(TripNode, TripNode),

			(WalkingNode, WalkingNode),
			(WaitingNode, WaitingNode),

			(WalkingNode, WaitingNode),
			(WaitingNode, WalkingNode)
		])

	@property
	def cumulative_duration(self) -> BaseDuration:
		"""
		"""
		if self._root is None:
			return Minutes(0)

		curr = self._root
		duration = curr.segment_edge.duration

		while curr.next is not None:
			curr = curr.next
			duration += curr.segment_edge.duration

		return duration
	
	@property
	def first_stop(self) -> Optional[Stop]:
		"""
		"""
		if self._root is None:
			return None
		return self._root.segment_edge.prv_node.stop
	
	@property
	def last_stop(self) -> Optional[Stop]:
		"""
		"""
		if self.last is None:
			return None
		return self.last.to_stop
	
	@property
	def returns_to_first_stop(self) -> bool:
		first = self.first_stop
		last = self.last_stop

		if (first is None) or (last is None):
			return False
		else:
			return first.standard_stop_name == last.standard_stop_name
	
	def is_within_time_limit(
		self,
		time_limit: BaseDuration
	) -> bool:
		"""
		"""
		return self.cumulative_duration < time_limit