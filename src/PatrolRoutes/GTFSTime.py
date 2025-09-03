"""
Subclass of int that is defined for postiive integers and has builtin
conversions between integer and GTFS time-since-midnight format. 
"""

from typing import overload, TypeVar


from .Duration import BaseDuration, Hours, Minutes, Seconds


class GTFSTime:
	_sec: int

	class InvalidGTFSTimeException(Exception):
		def __init__(
			self,
			time: int | str,
			reason: str
		) -> None:
			"""
			"""
			super().__init__(
				f"Invalid GTFS time {time}: {reason}"
			)

	def __init__(
		self,
		val: int | str
	) -> None:
		"""
		"""
		if isinstance(val, str):
			self._sec = self._parse_fstr(val)
		elif isinstance(val, int):
			self._sec = val
		else:
			raise self.InvalidGTFSTimeException(val, "Must be an integer.")
		
	@classmethod
	def _parse_fstr(
		cls,
		time_s: str
	) -> int:
		"""
		Helper that just gets the seconds value
		"""
		tokens = list(map(int, time_s.split(':')))

		if len(tokens) == 2:
			hours, minutes = tokens
			seconds = 0

		elif len(tokens) == 3:
			hours, minutes, seconds = tokens

		else:
			raise GTFSTime.InvalidGTFSTimeException(
				time_s,
				"Time strings must be 'HH:MM:SS' or 'HH:MM'."
			)
		
		return (hours*3600) + (minutes*60) + seconds

	@classmethod
	def from_fstr(
		cls,
		time_s: str
	) -> "GTFSTime":
		"""
		"""
		return cls(cls._parse_fstr(time_s))
	
	def to_fstr(
		self,
		short: bool = False,
		use_ampm: bool = False
	) -> str:
		"""
		Description
		___________
		Converts an internally represented time (seconds since midnight) to 
		a human-friendly string. 

		Parameters
		__________
		`time_i` : `int`
			An integer number of seconds since midnight.

		`short` : `bool`, default `False`
			If `True`, cut off the remainder seconds, whether they are 
			zero or not. 

		`use_ampm` : `bool`, default `False`
			if `True`, convert the hours to a 12-hour format and append
			'AM' or 'PM'. Suffix "AM-X" indicates the time extends into 
			the next calendar day.
		"""
		hours, remainder = divmod(self._sec, 3600)
		minutes, seconds = divmod(remainder, 60)

		suffix = ""

		if use_ampm:
			if hours <= 12:
				if hours == 12:
					suffix = " PM"
				else:
					suffix = " AM"

			elif 12 < hours < 24:
				suffix = " PM"
				hours = (hours % 12)

			elif 24 <= hours < 36:
				suffix = " AM-X"
				hours = (hours % 24)

			else:
				raise GTFSTime.InvalidGTFSTimeException(
					self._sec,
					(
						"The maximum time that can be represented with "
						"a 12-hour clock format is 35:59:59 (11:59:59 AM-X)."
					)
				)
			
		if short:
			return f"{hours:02}:{minutes:02}{suffix}"
		else:
			return f"{hours:02}:{minutes:02}:{seconds:02}{suffix}"
		
	def __eq__(self, other: "GTFSTime|int") -> bool:
		if isinstance(other, GTFSTime):
			return self._sec == other._sec
		else:
			return self._sec == other
	
	def __str__(self) -> str:
		return self.to_fstr()
	
	def __hash__(self) -> int:
		return hash(repr(self))
	
	def __int__(self) -> int:
		return self._sec
	
	def __repr__(self) -> str:
		return f'GTFSTime({self._sec}|"{self.to_fstr()}")'
	
	def __ge__(self, other: "GTFSTime") -> bool:
		return self._sec >= other._sec
	
	def __gt__(self, other: "GTFSTime") -> bool:
		return self._sec > other._sec
	
	def __le__(self, other: "GTFSTime") -> bool:
		return self._sec <= other._sec
	
	def __lt__(self, other: "GTFSTime") -> bool:
		return self._sec < other._sec
	
	def __add__(
		self,
		other: "GTFSTime|BaseDuration"
	) -> "GTFSTime":
		"""
		"""
		return GTFSTime(self._sec + other._sec)
	
	def __sub__(
		self,
		other: "GTFSTime|BaseDuration"
	) -> "BaseDuration":
		"""
		"""
		return Seconds(self._sec - other._sec)
	
	def __mul__(
		self,
		other: None
	) -> None:
		"""
		"""
		raise RuntimeError("Multiplication is not defined for GTFSTime")
	
	def __floordiv__(
		self,
		other: None
	) -> None:
		"""
		"""
		raise RuntimeError("Division is not defined for GTFSTime")
	
	def __rfloordiv__(
		self,
		other: None
	) -> None:
		"""
		"""
		raise RuntimeError("Division is not defined for GTFSTime")
	
	def __truediv__(
		self,
		other: None
	) -> None:
		"""
		"""
		raise RuntimeError("Division is not defined for GTFSTime")
	
	def __rtruediv__(
		self,
		other: None
	) -> None:
		"""
		"""
		raise RuntimeError("Division is not defined for GTFSTime")

"""
class _GTFSTime(int):
	###
	#GTFSTime is an integer with restrictions on operations, positivity,
	#and concise comparison API. 
	###
	class InvalidGTFSTimeException(Exception):
		def __init__(
			self,
			time: int | str,
			reason: str
		) -> None:
			###
			###
			super().__init__(
				f"Invalid GTFS time {time}: {reason}"
			)

	def __new__(
		cls,
		time_val: str | BaseDuration
	) -> "GTFSTime":
		###
		https://stackoverflow.com/questions/3238350/subclassing-int-in-python
		###

		if isinstance(time_val, str):
			conv = cls.from_fstr(time_val)
		else:
			conv = int(time_val)

		if conv < 0:
			raise GTFSTime.InvalidGTFSTimeException(
				conv,
				"Time values cannot be negative."
			)

		return super(cls, cls).__new__(cls, conv)
	
	def __eq__(self, other: "GTFSTime|BaseDuration") -> bool:
		return int(self) == int(other)
	
	def __str__(self) -> str:
		return str(int(self))
	
	def __repr__(self) -> str:
		return f'GTFSTime({self}|"{self.to_fstr()}")'

	def __add__(
		self,
		other: "GTFSTime|BaseDuration"
	) -> "GTFSTime":
		###
		###
		return GTFSTime(Seconds(int(self)) + Seconds(int(other)))
	
	def __sub__(
		self,
		other: "GTFSTime|BaseDuration"
	) -> "GTFSTime":
		###
		###
		return GTFSTime(Seconds(int(self)) - Seconds(int(other)))
	
	def __mul__(
		self,
		other: None
	) -> None:
		###
		###
		raise RuntimeError("Multiplication is not defined for GTFSTime")
	
	def __floordiv__(
		self,
		other: None
	) -> None:
		###
		###
		raise RuntimeError("Division is not defined for GTFSTime")
	
	def __rfloordiv__(
		self,
		other: None
	) -> None:
		###
		###
		raise RuntimeError("Division is not defined for GTFSTime")
	
	def __truediv__(
		self,
		other: None
	) -> None:
		###
		###
		raise RuntimeError("Division is not defined for GTFSTime")
	
	def __rtruediv__(
		self,
		other: None
	) -> None:
		###
		###
		raise RuntimeError("Division is not defined for GTFSTime")

	@classmethod
	def from_fstr(
		cls,
		time_s: str
	) -> "GTFSTime":
		###
		###
		tokens = list(map(int, time_s.split(':')))

		if len(tokens) == 2:
			hours, minutes = tokens
			seconds = 0

		elif len(tokens) == 3:
			hours, minutes, seconds = tokens

		else:
			raise GTFSTime.InvalidGTFSTimeException(
				time_s,
				"Time strings must be 'HH:MM:SS' or 'HH:MM'."
			)
		
		return cls(Seconds((hours*3600) + (minutes*60) + seconds))
	
	def to_fstr(
		self,
		short: bool = False,
		use_ampm: bool = False
	) -> str:
		###
		Description
		___________
		Converts an internally represented time (seconds since midnight) to 
		a human-friendly string. 

		Parameters
		__________
		`time_i` : `int`
			An integer number of seconds since midnight.

		`short` : `bool`, default `False`
			If `True`, cut off the remainder seconds, whether they are 
			zero or not. 

		`use_ampm` : `bool`, default `False`
			if `True`, convert the hours to a 12-hour format and append
			'AM' or 'PM'. Suffix "AM-X" indicates the time extends into 
			the next calendar day.
		###
		hours, remainder = divmod(self, 3600)
		minutes, seconds = divmod(remainder, 60)

		suffix = ""

		if use_ampm:
			if hours <= 12:
				if hours == 12:
					suffix = " PM"
				else:
					suffix = " AM"

			elif 12 < hours < 24:
				suffix = " PM"
				hours = (hours % 12)

			elif 24 <= hours < 36:
				suffix = " AM-X"
				hours = (hours % 24)

			else:
				raise GTFSTime.InvalidGTFSTimeException(
					self,
					(
						"The maximum time that can be represented with "
						"a 12-hour clock format is 35:59:59 (11:59:59 AM-X)."
					)
				)
			
		if short:
			return f"{hours:02}:{minutes:02}{suffix}"
		else:
			return f"{hours:02}:{minutes:02}:{seconds:02}{suffix}"
"""