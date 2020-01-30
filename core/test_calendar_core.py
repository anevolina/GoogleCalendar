import unittest
from datetime import datetime


from main_api import get_start_end_time
import calendar_core

class CalendarCoreTest(unittest.TestCase):

    def test_get_start_end_time(self):
        """Test parsing start and end time from a given string to datetime format"""

        start1, end1 = get_start_end_time('27 Jul 2019 11 a.m.')
        start2, end2 = get_start_end_time('April 19 2018 at 6 p.m.', 0.5)
        start3, end3 = get_start_end_time('June')

        self.assertEqual((start1, end1), (datetime(year=2019, month=7, day=27, hour=11, minute=0),
                                          datetime(year=2019, month=7, day=27, hour=12, minute=0)))

        self.assertEqual((start2, end2), (datetime(year=2018, month=4, day=19, hour=18, minute=0),
                                          datetime(year=2018, month=4, day=19, hour=18, minute=30)))

        self.assertEqual((start3, end3), (datetime.now().date(), datetime.now().date()))

    def test_get_update_sql_text(self):
        """Test sql formatting"""

        param1 = calendar_core.get_update_sql_text(credentials='value_credentials', calendar_id='123')
        param2 = calendar_core.get_update_sql_text(time_zone='Nicosia/Cyprus')

        self.assertEqual(param1,'credentials = excluded.credentials,\ncalendar_id = excluded.calendar_id')
        self.assertEqual(param2, 'time_zone = excluded.time_zone')



if __name__ == '__main__':
    unittest.main()