"""
Shape representation. Contains sequence of line segments that specify
what direction they are traveling to be used in instructions (e.g. POIs)

See planning docstring notes in POI.py
"""
 
from dataclasses import dataclass
from enum import Enum
import io
import numpy as np
import pandas as pd
from pathlib import Path
from typing import (
	Any, cast, Dict, Generic, List, Optional, overload, 
	TYPE_CHECKING, Type, TypedDict, TypeVar, TypeAlias
)

from .Utils import Point
from .POI import POI, POIs
from .PolygonBoundary import LineSegment
from .Stops import Stops, Stop
from .Utils import Point
from .Utils import RightLeftEnum as RL

if TYPE_CHECKING:
	from .Trips import Trips, Trip


class ShapeFeatureDistException(Exception):
	def __init__(
		self,
		shape_segment: "ShapeSegment",
		entity: Any,
		distance: float,
		tolerance: float
	) -> None:
		"""
		"""
		super().__init__(
			f"Tried to add '{entity}' as a feature to {shape_segment} but it is "
			f"{distance:.4f} miles away (tolerance: {tolerance})."
		)


class KnownShapeFeatureException(Exception):
	def __init__(
		self,
		shape: "Shape",
		entity: Any
	) -> None:
		"""
		"""
		super().__init__(f"{shape} already contains entity {entity}.")


NP_T: TypeAlias = "Optional[ShapeFeature]"
class SFChainException(Exception):
	def __init__(
		self,
		prv: NP_T,
		cur: NP_T,
		nxt: NP_T
	) -> None:
		"""
		"""
		prv_nxt = prv.next if prv is not None else None
		cur_prv = cur.prev if cur is not None else None
		cur_nxt = cur.next if cur is not None else None
		nxt_prv = nxt.prev if nxt is not None else None

		super().__init__(
			f"Problem with linking the following ShapeFeatures:\n"
			f"- Previous: {prv} (previous.next = {prv_nxt})\n"
			f"- Current: {cur} (previous = {cur_prv}, next = {cur_nxt})\n"
			f"- Next: {nxt} (previous = {nxt_prv})"
		)


SF_T = TypeVar("SF_T")
class ShapeFeature(Generic[SF_T]):
	"""
	Uniform container for any entity that has a location
	and can be associated with or projected onto a shape (segment). 
	"""
	_sf_id: int = 0

	_obj: SF_T
	_real_loc: Point
	_proj_loc: Point
	_shape_dist_traveled: float

	_nxt: NP_T
	_prv: NP_T

	def __init__(
		self,
		entity: SF_T,
		real_location: Point,
		projected_location: Point,
		shape_dist_traveled: float
	) -> None:
		"""
		"""
		self._obj = entity
		self._real_loc = real_location
		self._proj_loc = projected_location
		self._shape_dist_traveled = shape_dist_traveled

		self._sf_id = ShapeFeature._sf_id
		ShapeFeature._sf_id += 1

		self._nxt = None
		self._prv = None

	def __str__(self) -> str:
		return (
			f"ShapeFeature {self._sf_id} containing {self._obj} "
			f"(shape distance traveled = {self._shape_dist_traveled})"
		)
	
	def __repr__(self) -> str:
		return (
			f"ShapeFeature(id={self._sf_id}, entity={self._obj!r}, "
			f"shape_dist_traveled={self._shape_dist_traveled})"
		)

	@property
	def entity(self) -> SF_T: return self._obj
	@property
	def real_location(self) -> Point: return self._real_loc
	@property
	def projected_location(self) -> Point: return self._proj_loc
	@property
	def id(self) -> int: return self._sf_id

	@property
	def prev(self) -> NP_T: return self._nxt
	@prev.setter
	def prev(self, node: NP_T) -> None: self._prv = node

	@property
	def next(self) -> NP_T: return self._nxt
	@next.setter
	def next(self, node: NP_T) -> None: self._nxt = node

	@classmethod
	def _compare_shape_dist(
		cls,
		node1: NP_T,
		op: str,
		node2: NP_T
	) -> bool:
		if (node1 is None) or (node2 is None):
			return False

		try:
			return eval(
				f"{node1._shape_dist_traveled}{op}{node2._shape_dist_traveled}"
			)
		except SyntaxError:
			raise ValueError(f"Invalid operation for comparing floats: '{op}'")
		
	### Functions for treating ShapeFeatures as nodes in a chain ordered by 
	### increasing shape_distance_traveled. 

	@classmethod
	def nodes_not_none_and_in_order(
		cls,
		nodes: "List[NP_T]"
	) -> bool:
		"""
		"""
		if any([n is None for n in nodes]):
			return False
		
		for i in range(len(nodes)-1):
			if ShapeFeature._compare_shape_dist(nodes[i], '>', nodes[i+1]):
				return False
			
		return True

		
	def _insert_between(
		self,
		prv: NP_T,
		nxt: NP_T
	) -> None:
		"""
		Alters links in the following possible ways (before/after):
		
		- `prv` -> `nxt` ==> `prv` -> `self` -> `nxt`
		- `prv` is `None` ==> `self` -> `nxt`
		- `nxt` is `None` ==> `prv` -> `self`
		"""
		if (prv is None) and (nxt is None):
			raise SFChainException(prv, self, nxt)
		
		if (prv is not None) and (nxt is not None):
			## If both exist, they must be connected already
			if (prv.next is not nxt) or (nxt.prv is not prv):
				raise SFChainException(prv, self, nxt)
		
		if prv is not None:
			prv.next = self
			self.prv = prv

		if nxt is not None:
			nxt.prv = self
			self.next = nxt


	@classmethod
	def insert_and_get_first_node(
		cls,
		new_node: "ShapeFeature",
		first_node: "ShapeFeature"
	) -> "ShapeFeature":
		"""
		Returns the first node, which may change depending on distance
		"""
		if ShapeFeature._compare_shape_dist(new_node, '<', first_node):
			new_node._insert_between(None, first_node)
			return new_node
		
		cand_prv = first_node
	
		while cand_prv.next is not None:
			cand_prv = cand_prv.next
			cand_order = [cand_prv, new_node, cand_prv.next]

			if ShapeFeature.nodes_not_none_and_in_order(cand_order):
				new_node._insert_between(cand_prv, cand_prv.next)
				return first_node

		## if we got here, node still hasn't been inserted which means it 
		## belongs either last or second to last
		if ShapeFeature._compare_shape_dist(new_node, '>', cand_prv):
			new_node._insert_between(cand_prv, None)
		else:
			new_node._insert_between(cand_prv.prev, cand_prv)

		return first_node


class _ShapeRow(TypedDict):
	shape_id: str
	shape_pt_lat: float
	shape_pt_lon: float
	shape_pt_sequence: int
	shape_dist_traveled: float


class ShapePoint(Point):
	_shape_dist_traveled: float

	def __init__(
		self,
		shape_row: _ShapeRow
	) -> None:
		"""
		"""
		super().__init__((
			shape_row["shape_pt_lat"],
			shape_row["shape_pt_lon"]
		))

		self._shape_dist_traveled = shape_row["shape_dist_traveled"]

	@property
	def shape_dist_traveled(self) -> float: return self._shape_dist_traveled


class ShapeSegment:
	_shape_id: str
	_shape_seg_num: int

	#_prv: "Optional[ShapeSegment]"
	#_nxt: "Optional[ShapeSegment]"

	_lseg: LineSegment[ShapePoint, ShapePoint]

	_feat_d: Dict[int, ShapeFeature] ## int is ShapeFeature ID

	def __init__(
		self,
		shape_id: str,
		shape_seg_num: int,
		start_row: _ShapeRow,
		end_row: _ShapeRow,
	) -> None:
		"""
		"""
		self._shape_id = shape_id
		self._shape_seg_num = shape_seg_num

		self._prv = None
		self._nxt = None

		start_pt = ShapePoint(start_row)
		end_pt = ShapePoint(end_row)

		self._lseg = LineSegment.new_line_segment(
			start_pt,
			end_pt
		)

		self._feat_d = {}

	def __str__(self) -> str:
		"""
		"""
		return (
			f"shape {self._shape_id} segment {self._shape_seg_num} "
			f"({self._lseg})"
		)
	
	@property
	def start(self) -> ShapePoint: return self._lseg.p1
	@property
	def end(self) -> ShapePoint: return self._lseg.p2
	@property
	def shape_dist_length(self) -> float: 
		return self.end.shape_dist_traveled - self.start.shape_dist_traveled
	
	#@property
	#def next(self) -> "Optional[ShapeSegment]": return self._nxt
	#@next.setter
	#def next(self, nxt: "ShapeSegment"): self._nxt = nxt

	#@property
	#def prev(self) -> "Optional[ShapeSegment]": return self._prv
	#@prev.setter
	#def prev(self, prv: "ShapeSegment"): self._prv = prv

	def get_projected_distance(
		self,
		real_location: Point
	) -> float:
		"""
		Gets how far a point would move to be projected onto
		this line segment. 
		"""
		proj_pt = self._lseg.project_point(
			real_location,
			bounded = False
		)

		return real_location.distance_to(proj_pt)
	
	def get_projected_point(
		self,
		point: Point
	) -> Point:
		"""
		"""
		return self._lseg.project_point(point, bounded=False)
 	
	def add_feature(
		self,
		new_sf: ShapeFeature
	) -> None:
		"""
		"""		
		self._feat_d[new_sf.id] = new_sf

	def _get_prior_sf_stop(
		self,
		sf_poi: ShapeFeature[POI],
		sf_poi_ind: int
	) -> ShapeFeature[Stop]:
		"""
		"""
		## first check if this segment
		
		raise NotImplementedError


	def get_all_poi_feature_instructions(
		self
	) -> Optional[List[str]]:
		"""
		Returns list of instructions for any SF[POI]
		"""
		if len(self._feat_d) == 0:
			return None

		instructions: List[str] = []

		sf_sorted = sorted(
			list(self._feat_d.values()),
			key = lambda sf: sf._shape_dist_traveled
		)

		for i, sf in enumerate(sf_sorted):
			if not isinstance(sf.entity, POI):
				continue
			
			look_direction = self.get_relative_point_side(sf.real_location)
			


		raise NotImplementedError
	
	def get_relative_point_side(
		self,
		point: Point
	) -> RL:
		"""
		Gets whether to look left or right in the direction of travel 
		(increasing shape_dist_traveled) to observe a given point.

		Compute angle between lseg and segment formed by starting point
		and query point. If positive, return RL
		"""
		angle = self._lseg.get_angle_with(point)

		if angle < 0:
			return RL.LEFT
		else:
			return RL.RIGHT


class Shape:
	_shape_id: str
	_err_tol: float

	_segs: List[ShapeSegment]

	_entity_to_sf_d: Dict[int|str, ShapeFeature] ## key is ID for the object in ShapeFeature
	#_sf_to_seg_d: Dict[int, ShapeSegment] ## key is ShapeFeature ID, value is segment it's on
	_first_sf: Optional[ShapeFeature] ## ShapeFeature linked list

	def __init__(
		self,
		shape_id: str,
		shape_rows: List[_ShapeRow],
		shape_feature_max_error
	) -> None:
		"""
		"""
		self._shape_id = shape_id
		self._err_tol = shape_feature_max_error

		self._segs = []
		self._entity_to_sf_d = {}
		#self._sf_to_seg_d = {}

		for i in range(len(shape_rows)-1):
			self._segs.append(
				ShapeSegment(
					self._shape_id,
					i,
					shape_rows[i],
					shape_rows[i+1]
				)
			)
		
		## Set prv
		#for i in range(1, len(self._segs)):
		#	self._segs[i].prev = self._segs[i-1]

		## Set nxt
		#for i in range(0, len(self._segs) - 1):
		#	self._segs[i].next = self._segs[i+1]

	def __str__(self) -> str: return f"shape {self._shape_id}"

	def __repr__(self) -> str: return f"Shape(_shape_id={self._shape_id})"
	
	def add_feature(
		self,
		entity: Any,
		entity_id: int|str,
		entity_real_location: Point
	) -> None:
		"""
		"""
		## Check if already added this entity
		try:
			self._entity_to_sf_d[entity_id]
			raise KnownShapeFeatureException(self, entity)
		except KeyError:
			pass

		## Find closest segment to entity
		seg_proj_dists = [
			self._segs[i].get_projected_distance(entity_real_location)
			for i in range(len(self._segs))
		]

		seg_proj_dist = min(seg_proj_dists)
		seg_num = seg_proj_dists.index(seg_proj_dist)
		seg = self._segs[seg_num]

		## Check if closest segment within shape separation tolerance
		if seg_proj_dist > self._err_tol:
			raise ShapeFeatureDistException(
				seg,
				entity,
				seg_proj_dist,
				self._err_tol
			)
		
		## Project entity onto shape and calculate shape distance traveled
		## at the point when the vehicle reaches the entity.
		seg_proj_point = seg.get_projected_point(entity_real_location)
		
		real_dist_ratio = (
			seg.start.distance_to(seg_proj_point)
			/ seg.start.distance_to(seg.end)
		)

		proj_point_shape_dist_traveled = seg.start.shape_dist_traveled + (
			 seg.shape_dist_length * real_dist_ratio
		)
		
		## Instantiate shape feature and insert into appropriate ShapeSegment
		## and record-keeping dicts
		new_sf = ShapeFeature(
			entity,
			entity_real_location,
			seg_proj_point,
			proj_point_shape_dist_traveled
		)

		seg.add_feature(new_sf)
		self._entity_to_sf_d[seg_num] = new_sf
		self._sf_to_seg_d[new_sf.id] = seg


	def get_all_poi_instructions(
		self,
		begin_stop: Stop,
		end_stop: Stop
	) -> Optional[List[str]]:
		"""
		end_stop is inclusive
		"""

		raise NotImplementedError
	
	@overload
	def draw_shape(self, outpath: Path) -> None: ...
	@overload
	def draw_shape(self, outpath: None) -> io.BytesIO: ...
	def draw_shape(
		self,
		outpath: Optional[Path] = None
	) -> Optional[io.BytesIO]:
		"""
		If outpath is None, return a bytes object with figure, otherwise
		save image to file and return None.

		`p.save(img_bytes_io, format='png')` (Google AI search
		for "plotnine get png bytes")
		"""
		raise NotImplementedError
	

class UnknownShapeException(Exception):
	def __init__(self, shape_id: str) -> None:
		super().__init__(
			f"Unknown shape ID '{shape_id}'."
		)
	

class Shapes:
	_shape_id_d: Dict[str, Shape]
	_err_tol: float

	def __init__(
		self,
		shapes_path: Path,
		shape_feature_max_error: float = 0.02
	) -> None:
		"""
		"""
		self._shape_id_d = {}
		self._err_tol = shape_feature_max_error

		raw_rows_d: Dict[str, List[_ShapeRow]] = {}

		shapes_df = pd.read_csv(shapes_path)

		for _, row in shapes_df.iterrows():
			shapes_row = cast(_ShapeRow, row)
			try:
				raw_rows_d[shapes_row['shape_id']].append(shapes_row)
			except KeyError:
				raw_rows_d[shapes_row['shape_id']] = [shapes_row]

		for shape_id, shape_rows in raw_rows_d.items():
			self._shape_id_d[shape_id] = Shape(
				shape_id, 
				shape_rows,
				shape_feature_max_error = self._err_tol
			)

	def __getitem__(
		self,
		shape_id: str
	) -> Shape:
		"""
		"""
		try:
			return self._shape_id_d[shape_id]
		except KeyError:
			raise UnknownShapeException(shape_id)
	
	def get_all_poi_instructions(
		self,
		shape_id: str,
	) -> Optional[List[str]]:
		"""
		"""
		return self._shape_id_d[shape_id].get_all_poi_instructions()