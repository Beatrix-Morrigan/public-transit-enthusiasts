"""
Classes to manage what services are on each date and including exceptions
for holidays. 
"""


from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
import pandas as pd
from pathlib import Path
from typing import Callable, Dict, List, Literal


from .Utils import append_to_dict_of_lists, insert_in_dict_of_dicts


class ServExcepEnum(Enum):
	SERVICE_ADDED = 1
	SERVICE_REMOVED = 2

	@classmethod
	def get(cls, val: Literal[1]|Literal[2]) -> "ServExcepEnum":
		if val == 1:
			return cls.SERVICE_ADDED
		elif val == 2:
			return cls.SERVICE_REMOVED
		else:
			raise ValueError(
				f"Unknown value for ServiceExceptionEnum ({val})."
			)
		
class Service:
	_gtfs_strf: str = "%Y%m%d"

	_svc_excep: "ServiceExceptions"

	_service_id: str
	_service_days: "DateServices._ServiceDays"
	_start_date: datetime
	_end_date: datetime
	_service_name: str

	_is_in_service: Dict[str, bool]

	def __init__(
		self,
		calendar_row: pd.Series,
		svc_excp: "ServiceExceptions"
	) -> None:
		"""
		"""
		self._svc_excep = svc_excp
		self._is_in_service = {}
		self._service_id = calendar_row.iloc[0]
		
		self._service_days = DateServices._ServiceDays(
			*[
				self._service_id
			] + [
				[
					self._parse_day(elem) 
					for elem in calendar_row.to_list()[1:8]
				]
			] # type: ignore
		)

		self._start_date = datetime.strptime(
			str(calendar_row.iloc[8]),
			self._gtfs_strf
		)

		self._end_date = datetime.strptime(
			str(calendar_row.iloc[9]),
			self._gtfs_strf
		)

		self._service_name = calendar_row.iloc[10]

		## Populate in service dates
		## https://stackoverflow.com/a/1060330/26707652

		n_days = (self._end_date - self._start_date).days

		for day_n in range(n_days):
			day = self._start_date + timedelta(day_n)

			is_regularly_scheduled = self._service_days.runs_on_day_of_week(
				day.weekday()
			)

			is_added = self._svc_excep.service_is_added(
				self.service_id, 
				day
			)

			is_removed = self._svc_excep.service_is_removed(
				self.service_id,
				day
			)

			self._is_in_service[day.strftime(self._gtfs_strf)] = (
				(is_regularly_scheduled and (not is_removed))
				or ((not is_regularly_scheduled) and is_added)
			)

	def _parse_day(self, s: Literal["0"]|Literal["1"]) -> bool: 
		return bool(int(s))
		
	def runs_on_date(
		self,
		service_date: date
	) -> bool:
		try:
			return self._is_in_service[
				service_date.strftime(self._gtfs_strf)
			]
		except KeyError:
			return False
	
	@property
	def service_id(self) -> str: return self._service_id


class ServiceExceptions:
	_gtfs_strf: str = "%Y%m%d"

	# {service_id: {datestr: 0|1}}
	_excep: Dict[str, Dict[str, "ServExcepEnum"]]

	def __init__(
		self,
		calendar_dates_path: Path
	) -> None:
		"""
		"""
		self._excep = {}

		df = pd.read_csv(calendar_dates_path)

		for _, row in df.iterrows():
			service_id = str(row.iloc[0])
			service_date = str(row.iloc[1])
			excep_type: ServExcepEnum = ServExcepEnum.get(
				row.iloc[2]
			)

			insert_in_dict_of_dicts(
				self._excep,
				service_id,
				service_date,
				excep_type
			)

	def _check_type(
		self,
		service_id: str,
		service_date: date,
		queried_excep_type: ServExcepEnum
	) -> bool:
		"""
		"""
		date_s = service_date.strftime(self._gtfs_strf)

		try:
			actual_excep_type = self._excep[service_id][date_s]
		except KeyError:
			return False
		
		return actual_excep_type == queried_excep_type
	
	def service_is_added(
		self,
		service_id: str,
		service_date: date
	) -> bool:
		"""
		"""
		return self._check_type(
			service_id,
			service_date,
			ServExcepEnum.SERVICE_ADDED
		)
	
	def service_is_removed(
		self,
		service_id: str,
		service_date: date
	) -> bool:
		"""
		"""
		return self._check_type(
			service_id,
			service_date,
			ServExcepEnum.SERVICE_REMOVED
		)


class DateServices:
	"""	
	A summary of calendar.txt and calendar_dates.txt listing each 
	day's service IDs. 
	"""
	_gtfs_strf: str = "%Y%m%d"

	_calendar_path: Path
	_calendar_dates_path: Path
	
	_svc_d: Dict[str, Service]
	_excep: ServiceExceptions

	@dataclass
	class _ServiceDays:
		_service_id: str
		_runs_day_of_week: List[bool] ## 0th is Monday, 6th is Sunday

		def runs_on_day_of_week(
			self,
			weekday_num: int
		) -> bool:
			"""
			This is not sufficient to determine if the trip actually runs
			because this class doesn't know the start and end dates of the
			service. 
			"""
			try:
				return self._runs_day_of_week[weekday_num]
			except IndexError:
				raise IndexError(
					f"Expected number between 0 (Monday) and 6 (Sunday), "
					f"got {weekday_num}."
				)

	def __init__(
		self,
		calendar_path: Path,
		calendar_dates_path: Path
	) -> None:
		"""
		"""
		self._calendar_path = calendar_path
		self._calendar_dates_path = calendar_dates_path

		self._excep = ServiceExceptions(
			self._calendar_dates_path
		)

		self._svc_d = {}

		calendar_df = pd.read_csv(str(self._calendar_path))

		for _, row in calendar_df.iterrows():
			new_svc = Service(row, self._excep)
			self._svc_d[new_svc.service_id] = new_svc

	def service_runs_on_date(
		self,
		service_id: str,
		service_date: date
	) -> bool:
		"""
		"""
		return self._svc_d[service_id].runs_on_date(service_date)
	
	def get_date_service_ids(
		self,
		service_date: datetime
	) -> List[str]:
		"""
		"""
		ret_svc_ids: List[str] = []

		for svc_id in self._svc_d.keys():
			try:
				if self._svc_d[svc_id].runs_on_date(service_date):
					ret_svc_ids.append(svc_id)
			except KeyError:
				continue

		return ret_svc_ids