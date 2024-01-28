#!/usr/bin/env python3
# ✓
import os

import pyowm

import calendar_tools
import serialize

TZ = calendar_tools.get_local_timezone()
OWM_API_KEY = os.getenv("OWM_API_KEY")
OWM_LOCATION = os.getenv("OWM_LOCATION")  # ex: "Berlin,DE"


def temp_to_thermometer(temp):
    if temp < 5:
        return "0"
    elif temp < 10:
        return "1"
    elif temp < 15:
        return "2"
    elif temp < 20:
        return "3"
    else:
        return "4"


def get_weather():
    owm = pyowm.OWM(OWM_API_KEY)
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(OWM_LOCATION)
    cw = observation.weather
    forecast = mgr.forecast_at_place(OWM_LOCATION, "3h").forecast
    forecast.actualize()

    return {
        "temp": cw.temperature("celsius")["temp"],
        "thermometer": temp_to_thermometer(cw.temperature("celsius")["temp"]),
        "sunrise_ts": cw.sunrise_time(timeformat="date").astimezone(TZ),
        "sunset_ts": cw.sunset_time(timeformat="date").astimezone(TZ),
        "status": cw.status if cw.status != "Rain" else cw.detailed_status.lower(),
        "forecast": [
            {
                "temp": nw.temperature("celsius")["temp"],
                "thermometer": temp_to_thermometer(nw.temperature("celsius")["temp"]),
                "status": (
                    nw.status if nw.status != "Rain" else nw.detailed_status.lower()
                ),
                "start_ts": nw.reference_time(timeformat="date").astimezone(TZ),
            }
            for nw in forecast.weathers[:4]
        ],
    }


if __name__ == "__main__":
    print(serialize.serialize({"weather": get_weather()}))
