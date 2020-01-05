"""
This is scheduler for Learning.
"""

import datetime
import itertools
import time

DAY_OF_WEEKS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def events_generator(schedule: str, start_at: datetime):
    if not start_at:
        start_at = datetime.datetime.now()
    parts = schedule.split(',')
    schedule_elements = []
    for element in parts:
        element = element.strip()
        parts = element.split(' ')
        if len(parts) > 2:
            raise ValueError("Wrong schedule template")

        day_of_week = parts[0]
        if day_of_week.startswith('+'):
            dow_index = None
            day_incrementor = int(day_of_week[1:])
        else:
            try:
                dow_index = DAY_OF_WEEKS.index(day_of_week)
            except ValueError:
                raise ValueError(f"Unexpected daw of week {day_of_week}. Possible values are: {DAY_OF_WEEKS}")
            day_incrementor = None

        if len(parts) == 2:
            parsed = time.strptime(parts[1], "%H:%M")
            time_part = {
                'hour': parsed.tm_hour,
                'minute': parsed.tm_min,
                'second': 0,
                'microsecond': 0,
            }
        else:
            time_part = {
                'hour': start_at.hour,
                'minute': start_at.minute,
                'second': start_at.second,
                'microsecond': start_at.microsecond,
            }

        schedule_elements.append((dow_index, time_part, day_incrementor))

    current_day = start_at
    for schedule_element in itertools.cycle(schedule_elements):
        day_of_week, time_part, day_incrementor = schedule_element
        if day_incrementor is not None:
            current_day += datetime.timedelta(days=day_incrementor)
            current_day = current_day.replace(**time_part)
            yield current_day
        else:
            while day_of_week != current_day.weekday():
                current_day += datetime.timedelta(days=1)
            current_day = current_day.replace(**time_part)
            yield current_day
            current_day += datetime.timedelta(days=1)
