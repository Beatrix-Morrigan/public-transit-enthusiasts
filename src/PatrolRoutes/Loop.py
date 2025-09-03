"""
Build trips based on the segment graph
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Generic, Iterator, List, Optional, overload, TypeVar


from .GTFSTime import GTFSTime
from .motd import motd
from .Duration import BaseDuration, Hours, Minutes, Seconds
from .LoopNode import LoopNode, TripNode, WaitingNode, WalkingNode, LoopLL
from .Settings import Settings
from .SegmentGraph import SegmentGraph
from .SegmentGraph import Edge as SegmentEdge
from .SegmentGraph import TripEdge as SegmentTripEdge
from .SegmentGraph import TransferEdge as SegmentTransferEdge
from .Stops import Stop
from .Utils import RouteStyle as RS


class Loop:
	"""
	Representation of a single looping trip. 
	"""
	_loop_num: int
	_seed: int
	_sg: SegmentGraph
	_loop_max_dur: Optional[BaseDuration]
	_loop_min_dur: Optional[BaseDuration]
	_loop_min_seg: Optional[int]
	_trip_min_dur: Optional[BaseDuration]
	_consec_route_ok: bool

	_s: Settings

	_ll: LoopLL

	def __init__(
		self,
		loop_number: int,
		seed: int,
		sg: SegmentGraph,
		settings: Settings
	) -> None:
		"""
		"""
		self._loop_num = loop_number
		self._seed = seed
		self._sg = sg

		self._loop_max_dur = settings.loop_max_duration
		self._loop_min_dur = settings.loop_min_duration
		self._loop_min_seg = settings.loop_min_segments
		self._trip_min_dur = settings.trip_min_duration
		self._consec_route_ok = settings.allow_consecutive_same_route

		self._s = settings ## Save for route masking

	def __str__(self) -> str:
		#first_dep = self.first_departure_time.to_fstr(use_ampm=True)
		#last_arr = self.last_arrival_time.to_fstr(use_ampm=True)

		first = self._ll.root
		last = self._ll.last
		
		if (first is None) or (last is None):
			raise RuntimeError(
				f"Cannot print a Loop if it hasn't been built."
			)

		first_dep = first.from_departure_time.to_fstr(use_ampm = True)
		last_arr = last.to_arrival_time.to_fstr(use_ampm = True)

		nodes_l: List[LoopNode] = []
		route_tokens: List[str] = []

		node = self._ll.root
		while node is not None:
			if isinstance(node, TripNode):
				assert isinstance(node.segment_edge, SegmentTripEdge)
				route_tokens.append(
					RS(
						node.segment_edge.trip.route_id,
						self._s
					).route_name
				)

			nodes_l.append(node)
			node = node.next

		return f"""
		{motd}
		================================================
		------------------------------------------------

		Loop {self._loop_num} : {first_dep} - {last_arr}
		Start: {first.from_stop.stop_name}
		Route: {" -> ".join(route_tokens)}

		------------------------------------------------
		================================================
		""" + ''.join([str(node) for node in nodes_l])
	
	def get_signature(self) -> str:
		"""
		"""
		node_names: List[str] = []

		node = self._ll.root
		while node is not None:
			node_names.append(node.name)

		return '__'.join(node_names)
	
	def __eq__(self, other: object) -> bool:
		"""
		"""
		if not isinstance(other, Loop):
			return False
		
		return self.get_signature() == other.get_signature()
	
	def __hash__(self) -> int:
		"""
		"""
		return hash(self.get_signature())

	def _debug_print(self, msg, tabs = 0):
		#print(('\t'*tabs) + msg)
		return
	
	def _is_walking_edge(
		self,
		edge: SegmentTransferEdge,
	) -> bool:
		return edge.prv_node.stop.stop_id != edge.nxt_node.stop.stop_id
	
	def _is_waiting_edge(
		self,
		edge: SegmentTransferEdge
	) -> bool:
		return edge.prv_node.stop.stop_id == edge.nxt_node.stop.stop_id

	def _has_failed(
		self,
		last_node: LoopNode,
		tabs: int = 0
	) -> bool:
		"""
		"""
		## Check if maximum duration has been exceeded
		if self._loop_max_dur is not None:
			if self._ll.cumulative_duration > self._loop_max_dur:
				self._debug_print("Failed for exceeding max duration.", tabs)
				return True
			
		## Check if trip just added, check if it's too short
		if (self._trip_min_dur is not None) and (isinstance(last_node, TripNode)):
			if last_node.segment_edge.duration < self._trip_min_dur:
				return True
			
		## Check if consecutive trips on same route added
		if (not self._consec_route_ok) and isinstance(last_node, TripNode) and (last_node.segment_number > 1):
			assert last_node.prev is not None
			assert isinstance(last_node.prev.prev, TripNode)

			last_trip_node = last_node.prev.prev

			last_trip = last_trip_node.segment_edge.prv_node.trip
			curr_trip = last_node.segment_edge.prv_node.trip

			if last_trip.route_id == curr_trip.route_id:
				return True
		
		## No failure cases found
		return False
	
	def _is_complete(
		self,
		last_node: LoopNode
	) -> bool:
		"""
		"""
		if not isinstance(last_node, TripNode):
			return False
		
		if not self._ll.returns_to_first_stop:
			return False
		
		if self._loop_min_dur is not None:
			if self._ll.cumulative_duration < self._loop_min_dur:
				return False
			
		if self._loop_min_seg is not None:
			if last_node.segment_number < self._loop_min_seg:
				return False

		## No partial conditions matched, this loop is valid as long as
		## _has_failed() returns False	
		return True

	LOOP_T = TypeVar("LOOP_T", bound = TripNode|WaitingNode|WalkingNode)
	def _build_recursive(
		self,
		last_node: LOOP_T,
		rng: np.random.Generator,
		tabs: int = 0
	) -> Optional[LOOP_T]:
		"""
		"""
		if self._has_failed(last_node, tabs = tabs):
			return None
		
		if self._is_complete(last_node):
			return last_node
		
		nxt_seg_num = last_node._seg_num + 1
		curr_end_st = last_node._segment.nxt_node

		candidate_next_edges = curr_end_st.get_shuffled_next_edges(rng)

		if len(candidate_next_edges) == 0: ## no options
			self._debug_print("Failed for no more options", tabs = tabs)
			return None
		
		for candidate_next_edge in candidate_next_edges:
			if isinstance(candidate_next_edge, SegmentTripEdge):
				candidate_node = TripNode(
					self._loop_num,
					nxt_seg_num,
					candidate_next_edge,
					self._s
				)

			elif isinstance(candidate_next_edge, SegmentTransferEdge):
				self._debug_print("FOUND A TRANSFER EDGE", tabs = tabs)
				if self._is_waiting_edge(candidate_next_edge):
					candidate_node = WaitingNode(
						self._loop_num,
						nxt_seg_num,
						candidate_next_edge,
						self._s
					)

				elif self._is_walking_edge(candidate_next_edge):
					candidate_node = WalkingNode(
						self._loop_num,
						nxt_seg_num,
						candidate_next_edge,
						self._s
					)

				else:
					raise RuntimeError(
						f"Should never see this. Something wrong with waiting/walking logic"
					)
				
			else:
				raise ValueError("Shouldn't see this, problem parsing edge types")
			
			self._debug_print(f"Trying {candidate_node.name}", tabs = tabs)
			
			if not (isinstance(last_node, TripNode) ^ isinstance(candidate_node, TripNode)):
				self._debug_print("Failed for trying to be a consecutive trip node", tabs = tabs)
				continue

			self._ll.connect_nodes(last_node, candidate_node)

			checked_candidate = self._build_recursive(
				candidate_node,
				rng,
				tabs = tabs + 1
			)

			if checked_candidate is None:
				self._ll.disconnect_nodes(last_node, candidate_node)
			else:
				return last_node
			
		self._debug_print("Got through all options and they were bad", tabs = tabs)
		return None ## none of options worked

	def build(
		self,
		verbose = False
	) -> None:
		"""
		"""
		rng = np.random.default_rng(self._seed)

		trip_edges = np.asarray(self._sg.trip_edges)

		rng.shuffle(trip_edges)

		trip_edges = trip_edges.tolist()

		for trip_edge in trip_edges:
			self._ll = LoopLL()

			first_trip = TripNode(
				self._loop_num,
				1,
				trip_edge,
				self._s
			)
			self._ll.root = first_trip

			_ = self._build_recursive(
				first_trip,
				rng,
			)

			#if self._ll.root is not None:
			if (self._ll.last is not None) and self._is_complete(self._ll.last):
				return
			
			
		print("No valid trips under current constraints.")

			
