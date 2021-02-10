#!/usr/bin/env python3
# ✓
import os
from datetime import datetime

import pytz

import serialize

ICAL_FALLBACK_TZ = pytz.timezone("UTC")
TZ = os.getenv("TZ") or ICAL_FALLBACK_TZ


def generate_test_data():
    return {
        "weather": {
            "temp": 11.8,
            "sunrise": datetime(2020, 11, 14, 7, 27, 1, tzinfo=TZ),
            "sunset": datetime(2020, 11, 14, 16, 14, 52, tzinfo=TZ),
            "status": "clear sky",
            "forecast": [
                {
                    "temp": 11.15,
                    "status": "scattered clouds",
                    "ts": datetime(2020, 11, 14, 19, 0, tzinfo=TZ),
                },
                {
                    "temp": 10.63,
                    "status": "clear sky",
                    "ts": datetime(2020, 11, 14, 22, 0, tzinfo=TZ),
                },
                {
                    "temp": 10.03,
                    "status": "snow",
                    "ts": datetime(2020, 11, 15, 1, 0, tzinfo=TZ),
                },
                {
                    "temp": 9.76,
                    "status": "overcast clouds",
                    "ts": datetime(2020, 11, 15, 4, 0, tzinfo=TZ),
                },
            ],
        },
        "events": [
            {
                "ts": None,
                "title": (
                    "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. "
                    "Donec hendrerit tempor tellus. "
                    "Donec pretium posuere tellus. "
                    "Proin quam nisl, tincidunt et, mattis eget, convallis nec, purus. "
                    "Cum sociis natoque penatibus et magnis dis parturient montes, "
                    "nascetur ridiculus mus.  Nulla posuere.  Donec vitae dolor. "
                    "Nullam tristique diam non turpis. "
                    "Cras placerat accumsan nulla. "
                    "Nullam rutrum. "
                    " Nam vestibulum accumsan nisl."
                ),
            },
            {"ts": None, "title": "Document E-Paper Calendar"},
            {"ts": "13:37-23:42", "title": "FooBar!"},
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


if __name__ == "__main__":
    print(serialize.serialize(generate_test_data()))
