"""
Generate transit trips with specific time and segment constraints.
"""


import numpy as np
from pathlib import Path
import sys
from typing import Dict, Optional


from .Loop import Loop
from .SegmentGraph import SegmentGraph
from .Settings import Settings


sys.setrecursionlimit(2000)


class PatrolRoutes:
	_s: Settings
	_sg: SegmentGraph
	_loop_d: Dict[int, Loop]

	def __init__(
		self,
		settings_path: Path,
		build = True
	) -> None:
		"""
		"""
		self._s = Settings(settings_path)
		
		if build:
			if self._s.segment_graph_path is not None:
				try:
					self._sg = SegmentGraph.load(self._s.segment_graph_path)
				except FileNotFoundError:
					self._sg = SegmentGraph(self._s)
					self._sg.build_graph()
					self._sg.save(self._s.segment_graph_path)
				except EOFError:
					raise IOError(
						f"Unreadable SegmentGraph file {self._s.segment_graph_path}"
					)
			else:
				self._sg = SegmentGraph(self._s)
				self._sg.build_graph()

		self._loop_d = {}
	
	def run_interactive_demo(
		self,
		rng_seed: Optional[int] = 49
	) -> None:
		"""
		"""
		rng = np.random.default_rng(rng_seed)

		print("Interactive loop generation mode. This will run forever until you CTRL+C it.")

		loop_num = 0

		while True:
			new_loop = Loop(
				loop_num,
				rng.integers(low = 1, high = int(1e16)),
				self._sg,
				self._s
			)

			new_loop.build()

			print(str(new_loop))

			_ = input("Press ENTER to build the next loop.")

			loop_num += 1
			

	
