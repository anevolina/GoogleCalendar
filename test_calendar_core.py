import unittest
from datetime import datetime


from main_api import get_start_end_time

class CalendarCoreTest(unittest.TestCase):

    def test_get_start_end_time(self):

        start1, end1 = get_start_end_time('27 Jul 2019 11 a.m.')
        start2, end2 = get_start_end_time('April 19 2018 at 6 p.m.', 0.5)
        start3, end3 = get_start_end_time('June')

        self.assertEqual((start1, end1), (datetime(year=2019, month=7, day=27, hour=11, minute=0),
                                          datetime(year=2019, month=7, day=27, hour=12, minute=0)))

        self.assertEqual((start2, end2), (datetime(year=2018, month=4, day=19, hour=18, minute=0),
                                          datetime(year=2018, month=4, day=19, hour=18, minute=30)))

        self.assertEqual((start3, end3), (datetime.now().date(), datetime.now().date()))




if __name__ == '__main__':
    unittest.main()