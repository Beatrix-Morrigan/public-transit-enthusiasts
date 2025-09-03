from datetime import datetime
from pathlib import Path
import sys
import unittest


sys.path.insert(0, "../")
from src.PatrolRoutes import GTFS_STRF
from src.PatrolRoutes.GTFS import GTFS
from src.PatrolRoutes.GTFSTime import GTFSTime as GT


class GTFS_GTFS_tests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.gtfs = GTFS(Path("gtfs/MTS_JUN25/"))
	
	def test_date_trips(self):
		trips_on_july3rd = self.gtfs.get_date_trips( ## Thursday
			datetime.strptime("20250703", GTFS_STRF)
		)

		trips_on_july4th = self.gtfs.get_date_trips( ## Friday (Sunday service)
			datetime.strptime("20250704", GTFS_STRF)
		)

		trips_on_july5th = self.gtfs.get_date_trips( ## Saturday
			datetime.strptime("20250705", GTFS_STRF)
		)

		self.assertFalse(all([
			trip.route_id != "14"
			for trip in trips_on_july3rd
		]))

		self.assertTrue(all([
			trip.route_id != "14"
			for trip in trips_on_july4th
		]))

		self.assertTrue(all([
			trip.route_id != "14"
			for trip in trips_on_july5th
		]))

	def test_get_trip(self):
		self.assertEqual(
			self.gtfs.get_trip(18295023).route_id,
			"1"
		)

	def test_get_stop(self):
		self.assertEqual(
			self.gtfs.get_stop(12758).stop_name,
			"1st Av & Walnut Av"
		)

	def test_stoptimes_get_stop_stoptimes(self):
		self.assertEqual(
			len(self.gtfs.get_stop_stoptimes_on_date(
				datetime.strptime("20250721", GTFS_STRF), ## Monday
				11450
			)),
			13
		)

	def test_trip_first_stop(self):
		self.assertEqual(
			self.gtfs.get_trip(18295023).first_stoptime.stop_id,
			94048
		)

	def test_stop_stoptimes(self):
		self.assertEqual(
			self.gtfs.get_stop(94048).stop_times[0].departure_time,
			GT("05:03:00")
		)