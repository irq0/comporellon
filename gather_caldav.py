#!/usr/bin/env python3
# ✓
import itertools
import logging
import os
from datetime import datetime

import caldav
import vobject

import calendar_tools
import serialize

TZ = calendar_tools.get_local_timezone()
LOG = logging.getLogger(__name__)
CALDAV_URL = os.getenv("CALDAV_URL")
CALDAV_USER = os.getenv("CALDAV_USER")
CALDAV_PASSWORD = os.getenv("CALDAV_PASSWORD")
# ';'-separated list of calendar names; empty = no filter
CALDAV_CALENDARS = os.getenv("CALDAV_CALENDARS") or None


def caldav_today():
    def filter_fn(cal_name):
        if CALDAV_CALENDARS:
            return cal_name in CALDAV_CALENDARS.split(";")
        else:
            return True

    day_start = datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = datetime.now(TZ).replace(
        hour=23, minute=59, second=59, microsecond=999999
    )
    client = caldav.DAVClient(
        CALDAV_URL, username=CALDAV_USER, password=CALDAV_PASSWORD
    )
    principal = caldav.Principal(client, CALDAV_URL)
    LOG.info([cal.name for cal in principal.calendars()])
    todays_events = (
        cal.date_search(start=day_start, end=day_end)
        for cal in principal.calendars()
        if filter_fn(cal.name)
    )
    combined_cal = vobject.iCalendar()
    vevents = [
        event.vobject_instance.vevent for event in itertools.chain(*todays_events)
    ]
    combined_cal.contents["vevent"] = vevents
    return combined_cal


if __name__ == "__main__":
    try:
        calendar = caldav_today()
        formatted_events = [
            calendar_tools.format_event(event) for event in calendar.components()
        ]
        print(serialize.serialize({"events": formatted_events}))
    except Exception as e:
        print(
            serialize.serialize(
                {"events": [{"ts": None, "title": "CalDAV error: " + str(e)}]}
            )
        )
