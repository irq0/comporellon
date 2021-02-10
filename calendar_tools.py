#!/usr/bin/env python3
# ✓
import logging
import os
from datetime import date
from datetime import datetime
from datetime import time

import pytz


ICAL_FALLBACK_TZ = pytz.timezone("UTC")
TZ = os.getenv("TZ") or ICAL_FALLBACK_TZ
LOG = logging.getLogger(__name__)


def event_is_allday(event):
    return type(event.dtstart.value) == date and type(event.dtend.value) == date


def format_event(event):
    if event_is_allday(event):
        return {"ts": None, "title": event.summary.value}
    else:
        try:
            start = event.dtstart.value.astimezone(TZ).time().strftime("%H:%M")
        except Exception:
            start = "?"
        try:
            end = event.dtend.value.astimezone(TZ).time().strftime("%H:%M")
        except Exception:
            end = "?"

        return {
            "ts": f"{start}-{end}",
            "title": event.summary.value,
        }


def date_to_datetime_floor(dt):
    return datetime.combine(dt, time(0, 0, 0, 0, tzinfo=TZ))


def date_to_datetime_ceil(dt):
    return datetime.combine(dt, time(23, 59, 59, 999999, tzinfo=TZ))


def event_is_today(event):
    day_start = datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = datetime.now(TZ).replace(
        hour=23, minute=59, second=59, microsecond=999999
    )

    start = event.dtstart.value
    try:
        end = event.dtend.value
    except AttributeError:
        end = start

    if isinstance(start, date):
        start = date_to_datetime_floor(start)
    if isinstance(end, date):
        end = date_to_datetime_ceil(end)

    try:
        fallback_tz = event.dtstamp.value.tzinfo
    except Exception:
        fallback_tz = ICAL_FALLBACK_TZ

    if start.tzinfo is None:
        start = start.replace(tzinfo=fallback_tz)
    if end.tzinfo is None:
        end = end.replace(tzinfo=fallback_tz)

    try:
        if event.getrruleset() is not None:
            events = event.getrruleset().between(
                day_start.replace(tzinfo=None), day_end.replace(tzinfo=None), inc=True
            )
            return len(events) > 0
    except Exception:
        LOG.error("rrule failed:", exc_info=True)
        LOG.debug(
            {
                "start": start,
                "end": end,
            }
        )
        LOG.debug(event.contents)
        return False

    try:
        return (
            day_start <= start <= day_end
            or day_start <= end <= day_end
            or (start <= day_start and end >= day_end)
        )
    except Exception:
        LOG.error("Today check failed:", exc_info=True)
        LOG.debug(
            {
                "start": start,
                "end": end,
                "fallback_tz": fallback_tz,
            }
        )
        LOG.debug(event.contents)
