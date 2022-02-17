import unittest
from datetime import datetime

import vobject

import calendar_tools


class TestEventOn(unittest.TestCase):
    """Test calendar_tools.event_is_on"""

    def test_simple_start_end_event(self):
        tz = calendar_tools.get_local_timezone()
        day_before = datetime(2022, 2, 13, tzinfo=tz)
        day_event = datetime(2022, 2, 14, tzinfo=tz)
        day_after = datetime(2022, 2, 15, tzinfo=tz)
        event = next(
            vobject.readComponents(
                """BEGIN:VEVENT
DTSTART;TZID=Europe/Berlin:20220214T181500
DTEND;TZID=Europe/Berlin:20220214T191500
SUMMARY:Test
TRANSP:OPAQUE
END:VEVENT"""
            )
        )

        self.assertFalse(calendar_tools.event_is_on(event, day_before))
        self.assertTrue(calendar_tools.event_is_on(event, day_event))
        self.assertFalse(calendar_tools.event_is_on(event, day_after))

    def test_all_day_event(self):
        tz = calendar_tools.get_local_timezone()
        day_before = datetime(2022, 2, 14, tzinfo=tz)
        day_event = datetime(2022, 2, 15, tzinfo=tz)
        day_after = datetime(2022, 2, 16, tzinfo=tz)
        event = vobject.readOne(
            """BEGIN:VEVENT
DTSTART;VALUE=DATE:20220215
DTEND;VALUE=DATE:20220216
CLASS:PUBLIC
PRIORITY:5
SUMMARY:test all day
END:VEVENT"""
        )

        self.assertFalse(calendar_tools.event_is_on(event, day_before))
        self.assertTrue(calendar_tools.event_is_on(event, day_event))
        self.assertFalse(calendar_tools.event_is_on(event, day_after))

    def test_rrule(self):
        tz = calendar_tools.get_local_timezone()
        day_before = datetime(2022, 2, 13, tzinfo=tz)
        day_event = datetime(2022, 2, 14, tzinfo=tz)
        day_after = datetime(2022, 2, 15, tzinfo=tz)
        event = vobject.readOne(
            """BEGIN:VEVENT
RRULE:FREQ=WEEKLY;UNTIL=20220815T140000Z;INTERVAL=1;BYDAY=MO;WKST=SU
SUMMARY:Test
DTSTART;TZID=Europe/Berlin:20220124T160000
DTEND;TZID=Europe/Berlin:20220124T165000
SEQUENCE:94
END:VEVENT"""
        )

        self.assertFalse(calendar_tools.event_is_on(event, day_before))
        self.assertTrue(calendar_tools.event_is_on(event, day_event))
        self.assertFalse(calendar_tools.event_is_on(event, day_after))
