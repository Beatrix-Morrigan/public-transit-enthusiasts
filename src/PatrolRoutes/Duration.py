"""
Representations of elapsed time measured to the whole second. These will be 
used in place of plain integers throughout this code to protect against
time unit bugs, e.g. comparing minutes to seconds. 
"""


from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar
from typing_extensions import Self
import warnings


class BaseDuration(ABC):
	_sec: int  ## seconds
	_round_error_printed = False
	_c: Type[Self]

	def __init__(
		self,
		value: "int|float|BaseDuration"
	) -> None:
		"""
		"""
		self._c = self.__class__

		if isinstance(value, BaseDuration):
			self._sec = value._sec

		else:
			frac_val = value * self.scale
			self._sec = round(frac_val)
			
			if (frac_val != self._sec) and not BaseDuration._round_error_printed:
				warnings.warn(
					self.DurationRoundingWarning(
						frac_val,
						self
					)
				)
	
	@property
	@abstractmethod
	def scale(self) -> int|float:
		"""
		The number of whole seconds in one unit of time represented
		by the this class.
		"""
		pass

	@property
	@abstractmethod
	def unit_name_singular(self) -> str:
		"""
		Name of a single unit of time, e.g., 'minute', 'hour'.
		"""
		pass

	@property
	@abstractmethod
	def unit_name_plural(self) -> str:
		"""
		Name of multiple units of time, e.g., 'minutes', 'hours'.
		"""
		pass

	@property
	def unit_value(self) -> int|float:
		if self._sec % self.scale == 0:
			return int(self._sec/self.scale)
		else:
			return float(self._sec/self.scale)

	class DurationRoundingWarning(Warning):
		def __init__(
			self,
			frac_val: float,
			duration: "BaseDuration"
		) -> None:
			"""
			"""
			self._message = (
				f"'{type(duration)}' represents time in whole seconds. "
				f"Input value {frac_val} was rounded to "
				f"{duration._sec} seconds (). "
				f"This warning will be shown only once per session."
			)

		def __str__(self):
			BaseDuration._round_error_printed = True
			return repr(self._message)
	
	## Operations
	
	def __abs__(self) -> Self: return self._c(abs(self.unit_value))

	def __neg__(self) -> Self: return self._c(-self.unit_value)

	def __add__(self, other: "BaseDuration") -> Self:
		return self._c((self._sec + other._sec)/self.scale)
	
	#def __radd__(self, other: "BaseDuration") -> Self:
	#	return self.__add__(other)
	
	def __sub__(self, other: "BaseDuration") -> Self:
		return self._c((self._sec - other._sec)/self.scale)

	def __eq__(self, other: object) -> bool: 
		if not isinstance(other, BaseDuration):
			return False
		return self._sec == other._sec
	
	def __ne__(self, other: object) -> bool:
		if not isinstance(other, BaseDuration):
			return False
		return self._sec != other._sec
	
	def __ge__(self, other: "BaseDuration") -> bool:
		return self._sec >= other._sec
	
	def __gt__(self, other: "BaseDuration") -> bool:
		return self._sec > other._sec
	
	def __le__(self, other: "BaseDuration") -> bool:
		return self._sec <= other._sec
	
	def __lt__(self, other: "BaseDuration") -> bool:
		return self._sec < other._sec
	
	def __round__(self) -> "BaseDuration":
		return self._c(int(self._sec))
	
	def __mul__(self, other: float|int) -> "BaseDuration":
		return self._c((self._sec * other)/self.scale)
	
	def __rmul__(self, other: float|int) -> "BaseDuration":
		return self.__mul__(other)
	
	def __truediv__(self, other: float|int) -> "BaseDuration":
		return self._c((self._sec/other)/self.scale)
	
	def __floordiv__(self, other: float|int) -> "BaseDuration":
		return self._c(int(self._sec/other)/self.scale)
	
	def __repr__(self) -> str: 
		return (
			f"{self.__class__.__name__}(unit_value = {self.unit_value}, "
			f"seconds = {self._sec}, scale = {self.scale})"
		)
	
	def __str__(self) -> str:
		val = self.unit_value

		if val == 1:
			return f"{val} {self.unit_name_singular}"
		else:
			return f"{val} {self.unit_name_plural}"
		
	def __int__(self) -> int: return self._sec
		

class Hours(BaseDuration):
	@property
	def scale(self) -> int: return 3600
	@property
	def unit_name_singular(self) -> str: return "hour"
	@property
	def unit_name_plural(self) -> str: return "hours"

	
class Minutes(BaseDuration):
	@property
	def scale(self) -> int: return 60
	@property
	def unit_name_singular(self) -> str: return "minute"
	@property
	def unit_name_plural(self) -> str: return "minutes"


class Seconds(BaseDuration):
	@property
	def scale(self) -> int: return 1
	@property
	def unit_name_singular(self) -> str: return "second"
	@property
	def unit_name_plural(self) -> str: return "seconds"