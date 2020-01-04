from datetime import datetime
from unittest import TestCase

from study.logic import events_generator


class TestLogic(TestCase):

    def test_schedule_generator_increment_day(self):
        schedule = '+1'
        generator = events_generator(schedule, start_at=datetime(2020, 1, 4))
        self.assertEquals(next(generator), datetime(2020, 1, 5))
        self.assertEquals(next(generator), datetime(2020, 1, 6))
        self.assertEquals(next(generator), datetime(2020, 1, 7))

    def test_schedule_generator_increment_three_day(self):
        schedule = '+3 13:0'
        generator = events_generator(schedule, start_at=datetime(2020, 1, 4))
        self.assertEquals(next(generator), datetime(2020, 1, 7, 13))
        self.assertEquals(next(generator), datetime(2020, 1, 10, 13))
        self.assertEquals(next(generator), datetime(2020, 1, 13, 13))

    def test_schedule_generator_increment_one_day_three_day(self):
        schedule = '+1 15:00, +3 13:0'
        generator = events_generator(schedule, start_at=datetime(2020, 1, 4))
        self.assertEquals(next(generator), datetime(2020, 1, 5, 15))
        self.assertEquals(next(generator), datetime(2020, 1, 8, 13))
        self.assertEquals(next(generator), datetime(2020, 1, 9, 15))
        self.assertEquals(next(generator), datetime(2020, 1, 12, 13))

    def test_schedule_generator_one_day(self):
        schedule = 'Mon'
        generator = events_generator(schedule, start_at=datetime(2020, 1, 4))
        self.assertEquals(next(generator), datetime(2020, 1, 6))
        self.assertEquals(next(generator), datetime(2020, 1, 13))

    def test_schedule_generator_one_day_with_time(self):
        schedule = 'Mon 15:55'
        generator = events_generator(schedule, start_at=datetime(2020, 1, 4))
        self.assertEquals(next(generator), datetime(2020, 1, 6, 15, 55))
        self.assertEquals(next(generator), datetime(2020, 1, 13, 15, 55))

    def test_schedule_generator_two_days(self):
        schedule = 'Mon, Wed'
        generator = events_generator(schedule, start_at=datetime(2020, 1, 8))
        self.assertEquals(next(generator), datetime(2020, 1, 13))
        self.assertEquals(next(generator), datetime(2020, 1, 15))
        self.assertEquals(next(generator), datetime(2020, 1, 20))
        self.assertEquals(next(generator), datetime(2020, 1, 22))

    def test_schedule_generator_two_days_with_time(self):
        schedule = 'Sun 0:0, Wed 18:55'
        generator = events_generator(schedule, start_at=datetime(2020, 1, 8))
        self.assertEquals(next(generator), datetime(2020, 1, 12, 0, 0))
        self.assertEquals(next(generator), datetime(2020, 1, 15, 18, 55))
        self.assertEquals(next(generator), datetime(2020, 1, 19, 0, 0))
        self.assertEquals(next(generator), datetime(2020, 1, 22, 18, 55))
