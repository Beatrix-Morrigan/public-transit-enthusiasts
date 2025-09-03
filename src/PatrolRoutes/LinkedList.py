"""
Abstract class for one-one linked list nodes and linked list nodes
designed to contain a specific object.
"""

from abc import ABC, abstractmethod
from typing import Dict, Generic, Hashable, List, Optional, TypeVar, Tuple, Type
from typing_extensions import Self

O = Optional ## Going to be typing this a lot, no pun intended.


class InvalidConnectionException(Exception):
	def __init__(
		self, 
		node1: "BaseLLNode",
		node2: "BaseLLNode"
	) -> None:
		"""
		"""
		super().__init__(
			f"Cannot join {node1} and {node2}, node1.next is {node1.next} and "
			f"node2.prev is {node2.prev}, both must be None."
		)


class InvalidDisconnectionException(Exception):
	def __init__(
		self,
		node1: "BaseLLNode",
		node2: "BaseLLNode"
	) -> None:
		"""
		"""
		super().__init__(
			f"Cannot disconnect node1 and node2. Possible causes:\n"
			f"- node1.next is {node1.next}, should be node2 ({node2})\n"
			f"- node2.prev is {node2.prev}, should be node1 ({node1})\n"
			f"- node2.next is {node2.next}, should be None"
		)


"""
========================
= 	Linked Lists 	   =
========================
"""


PRV_T = TypeVar("PRV_T", bound = "BaseLLNode")
NXT_T = TypeVar("NXT_T", bound = "BaseLLNode")
class BaseLLNode(ABC, Generic[PRV_T, NXT_T]):
	_prv: O[PRV_T]
	_nxt: O[NXT_T]

	def __init__(
		self
	) -> None:
		self._prv = None
		self._nxt = None

	@abstractmethod
	def __str__(self) -> str:
		pass

	@property
	def prev(self) -> O[PRV_T]: return self._prv
	#@prev.setter
	#def prev(self, prev_node: PRV_T) -> None: self._prv = prev_node

	@property
	def next(self) -> O[NXT_T]: return self._nxt
	#@next.setter
	#def next(self, next_node: NXT_T) -> None: self._nxt = next_node


LLN_T = TypeVar("LLN_T", bound = "BaseLLNode")

class BaseLL(ABC, Generic[LLN_T]):
	_root: O[LLN_T]
	_inc: List[Tuple[Type[LLN_T], Type[LLN_T]]]

	def __init__(
		self,
		incompatible_links: O[List[Tuple[Type[LLN_T], Type[LLN_T]]]] = None
	) -> None:
		"""
		"""
		self._root = None
		if incompatible_links is None:
			self._inc = []
		else:
			self._inc = incompatible_links

	def _check_link_compatibility(
		self,
		node1: LLN_T,
		node2: LLN_T
	) -> bool:
		"""
		"""
		return not ((type(node1), type(node2)) in self._inc)

	@property
	def root(self) -> O[LLN_T]: 
		"""
		The first node that was added to this list
		"""
		return self._root
	@root.setter
	def root(self, node: LLN_T) -> None:
		if self._root is None:
			self._root = node
		else:
			raise RuntimeError(
				f"Cannot set root of this linked list to {node} "
				f"because it is already {self._root}."
			)
	
	@property
	def last(self) -> O[LLN_T]:
		"""
		"""
		if self._root is None:
			return None
		
		curr = self._root
		
		while curr.next is not None:
			curr = curr.next
		
		return curr
	
	def connect_nodes(
		self,
		node1: LLN_T,
		node2: LLN_T
	) -> None:
		"""
		Will add a directional edge from node1 to node2.
		"""
		if not ((node1._nxt is None) and (node2._prv is None)):
			raise InvalidConnectionException(node1, node2)
		
		node1._nxt = node2
		node2._prv = node1

	def disconnect_nodes(
		self,
		node1: LLN_T,
		node2: LLN_T
	) -> None:
		"""
		"""
		if (node1.next is not node2) or (node2.prev is not node1) or (node2.next is not None):
			raise InvalidDisconnectionException(node1, node2)
		
		node1._nxt = None
		node2._prv = None


"""
=============================
= 	Multiple  Linked Lists  =
=============================
"""

class MLLBaseNode(ABC, Generic[PRV_T, NXT_T]):
	_prv: Dict[Hashable, PRV_T]
	_nxt: Dict[Hashable, NXT_T]


