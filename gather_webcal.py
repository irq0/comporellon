#!/usr/bin/env python3
# ✓
import logging
import os

import requests
import vobject

import calendar_tools
import serialize

LOG = logging.getLogger(__name__)
# ';'-separated list of URLS pointing to iCal resources
WEBCAL_URLS = os.getenv("WEBCAL_URLS")


def get_ical(url):
    response = requests.get(url)
    if not response.ok:
        LOG.error(f"Failed to fetch {url}: {response.status_code}")
    cal = vobject.readOne(response.text)
    return [
        e
        for e in cal.components()
        if e.name == "VEVENT" and calendar_tools.event_is_today(e)
    ]


if __name__ == "__main__":
    formatted_events = []
    if WEBCAL_URLS:
        for url in WEBCAL_URLS.split(";"):
            formatted_events.extend(
                calendar_tools.format_event(event) for event in get_ical(url)
            )
    if formatted_events:
        print(serialize.serialize({"events": formatted_events}))
