#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import logging
import os
import os.path
import sys
from datetime import datetime, date, time

import caldav
import jinja2
import pyowm
import pytz
import vobject

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

TEMPLATE_PATH = os.path.dirname(os.path.realpath(__file__))
LOG = logging.getLogger(__name__)
TZ = os.getenv("TZ") or pytz.timezone("Europe/Berlin")
ICAL_FALLBACK_TZ = pytz.timezone("UTC")
OWM_API_KEY = os.getenv("OWM_API_KEY")
OWM_LOCATION = os.getenv("OWM_LOCATION")  ## ex: "Berlin,DE"
CALDAV_URL = os.getenv("CALDAV_URL")
CALDAV_USER = os.getenv("CALDAV_USER")
CALDAV_PASSWORD = os.getenv("CALDAV_PASSWORD")
# ';'-separated list of calendar names
CALDAV_CALENDARS = os.getenv("CALDAV_CALENDARS")

def get_weather():
    owm = pyowm.OWM(OWM_API_KEY)
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(OWM_LOCATION)
    cw = observation.weather
    forecast = mgr.forecast_at_place(OWM_LOCATION, "3h").forecast
    forecast.actualize()

    return {
        "temp": cw.temperature('celsius')["temp"],
        "sunrise": cw.sunrise_time(timeformat='date').astimezone(TZ),
        "sunset": cw.sunset_time(timeformat='date').astimezone(TZ),
        "status": cw.detailed_status.lower(),
        "forecast": [{
            "temp": nw.temperature('celsius')['temp'],
            "status": nw.detailed_status.lower(),
            "ts": nw.reference_time(timeformat='date').astimezone(TZ),
        } for nw in forecast.weathers[:4]]
    }

def event_is_allday(event):
    return isinstance(event.dtstart.value, date) and \
        isinstance(event.dtend.value, date)


def format_event(event):
    if event_is_allday(event):
        return {
            "ts": None,
            "title": event.summary.value
        }
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
            "ts": "{}-{}".format(start, end),
            "title": event.summary.value,
        }

def date_to_datetime_floor(dt):
    return datetime.combine(dt, time(0, 0, 0, 0, tzinfo=TZ))


def date_to_datetime_ceil(dt):
    return datetime.combine(dt, time(23, 59, 59, 999999, tzinfo=TZ))


def event_is_today(event):
    day_start = datetime.now(TZ).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0)
    day_end = datetime.now(TZ).replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=999999)

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
            events = event.getrruleset().between(day_start.replace(tzinfo=None),
                                                 day_end.replace(tzinfo=None),
                                                 inc=True)
            return len(events) > 0
    except Exception:
        LOG.error("rrule failed:", exc_info=True)
        LOG.debug({
            "start": start,
            "end": end,
        })
        LOG.debug(event.contents)
        return False

    try:
        return (day_start <= start <= day_end or
                day_start <= end <= day_end or
                (start <= day_start and end >= day_end))
    except Exception:
        LOG.error("Today check failed:", exc_info=True)
        LOG.debug({
            "start": start,
            "end": end,
            "fallback_tz": fallback_tz,
        })
        LOG.debug(event.contents)
def caldav_today(filter_fn=lambda x: True):
    day_start = datetime.now(TZ).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0)
    day_end = datetime.now(TZ).replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=999999)
    client = caldav.DAVClient(CALDAV_URL,
                              username=CALDAV_USER,
                              password=CALDAV_PASSWORD)
    principal = caldav.Principal(client, CALDAV_URL)
    LOG.info([cal.name for cal in principal.calendars()])
    todays_events = (cal.date_search(start=day_start,
                                     end=day_end)
                     for cal in principal.calendars()
                     if filter_fn(cal.name))
    combined_cal = vobject.iCalendar()
    vevents = [event.vobject_instance.vevent
               for event in itertools.chain(*todays_events)]
    combined_cal.contents["vevent"] = vevents
    return combined_cal

def mock():
    data = {
        'weather': {
            'temp': 11.8,
            'sunrise': datetime(2020, 11, 14, 7, 27, 1, tzinfo=TZ),
            'sunset': datetime(2020, 11, 14, 16, 14, 52, tzinfo=TZ),
            'status': 'clear sky',
            'forecast': [
                {
                    'temp': 11.15,
                    'status': 'scattered clouds',
                    'ts': datetime(2020, 11, 14, 19, 0, tzinfo=TZ)
                },
                {
                    'temp': 10.63,
                    'status': 'clear sky',
                    'ts': datetime(2020, 11, 14, 22, 0, tzinfo=TZ)
                },
                {
                    'temp': 10.03,
                    'status': 'snow',
                    'ts': datetime(2020, 11, 15, 1, 0, tzinfo=TZ)
                },
                {
                    'temp': 9.76,
                    'status': 'overcast clouds',
                    'ts': datetime(2020, 11, 15, 4, 0, tzinfo=TZ)
                }
            ]},
        'events': [
            {
                'ts': None,
                'title': 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit.  Donec hendrerit tempor tellus.  Donec pretium posuere tellus.  Proin quam nisl, tincidunt et, mattis eget, convallis nec, purus.  Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.  Nulla posuere.  Donec vitae dolor.  Nullam tristique diam non turpis.  Cras placerat accumsan nulla.  Nullam rutrum.  Nam vestibulum accumsan nisl.'
            },
            {
                'ts': None,
                'title': 'Document E-Paper Calendar'
            },
            {
                'ts': "13:37-23:42",
                'title': 'FooBar!'
            },
        ],
        "weather_icons": {
            "clear sky": r"\Sun",
            "few clouds": r"\SunCloud",
            "scattered clouds": r"\Cloud",
            "overcast clouds": r"\Cloud",
            "broken clouds": r"\Cloud",
            "shower rain": r"\RainCloud",
            "rain": r"\RainCloud",
            "light rain": r"\WeakRainCloud",
            "thunderstorm": r"\Lightning",
            "snow": r"\Snow",
            "mist": r"\Fog",
        },
    }

    LOG.info(data)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_PATH),
        block_start_string=r'\code{',
        block_end_string='}',
        variable_start_string=r'\jvar{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%!!',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
    )
    return env.get_template(sys.argv[1]).render(data)

def main():
    cal = caldav_today(filter_fn=lambda cal_name: cal_name in CALDAV_CALENDARS.split(";"))

    data = {
        "weather": get_weather(),
        "events": [format_event(e) for e in cal.components()
                   if event_is_today(e)],
        "weather_icons": {
            "clear sky": r"\Sun",
            "few clouds": r"\SunCloud",
            "scattered clouds": r"\Cloud",
            "overcast clouds": r"\Cloud",
            "broken clouds": r"\Cloud",
            "shower rain": r"\RainCloud",
            "rain": r"\RainCloud",
            "light rain": r"\WeakRainCloud",
            "thunderstorm": r"\Lightning",
            "snow": r"\Snow",
            "mist": r"\Fog",
        },
    }

    LOG.info(data)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_PATH),
        block_start_string=r'\code{',
        block_end_string='}',
        variable_start_string=r'\jvar{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%!!',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
    )
    return env.get_template(sys.argv[1]).render(data)

if __name__ == '__main__':
    if os.getenv("MOCK_DATA"):
        print(mock())
    else:
        print(main())
