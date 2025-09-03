from datetime import datetime
from pathlib import Path
import sys
import unittest


sys.path.insert(0, "../")
from src.PatrolRoutes import GTFS_STRF
from src.PatrolRoutes.GTFSService import DateServices


class GTFSService_DateService_tests(unittest.TestCase):

	def setUp(self):
		self.date_services = DateServices(
			Path("gtfs/MTS_JUN25/calendar.txt"),
			Path("gtfs/MTS_JUN25/calendar_dates.txt")
		)

	def test_in_service_checks(self):
		self.assertTrue(
			self.date_services.service_runs_on_date(
				"72985-0000001-0",
				datetime.strptime("20250126", GTFS_STRF)
			)
		)

		self.assertFalse(
			self.date_services.service_runs_on_date(
				"72985-0000001-0",
				datetime.strptime("20250127", GTFS_STRF)
			)
		)

		self.assertTrue(
			self.date_services.service_runs_on_date(
				"S2_84839-1111100-0",
				datetime.strptime("20250703", GTFS_STRF)
			)
		)

		self.assertFalse(
			self.date_services.service_runs_on_date(
				"S2_84839-1111100-0",
				datetime.strptime("20250704", GTFS_STRF)
			)
		)