#!/usr/bin/env python3
# ✓
import serialize

print(
    serialize.serialize(
        {
            "thermometer_icons": {
                0: "\\faThermometerEmpty",
                1: "\\faThermometerQuarter",
                2: "\\faThermometerHalf",
                3: "\\faThermometerThreeQuarters",
                4: "\\faThermometerFull",
            },
            "weather_icons": {
                "Thunderstorm": "\\Lightning",
                "Drizzle": "\\faCloudRain",
                "Rain": "\\faCloudShowersHeavy",
                "light rain": "\\faCloudSunRain",
                "moderate rain": "\\faCloudSunRain",
                "heavy intensity rain": "\\faCloudSunRain",
                "very heavy rain": "\\faCloudSunRain",
                "extreme rain": "\\faCloudSunRain",
                "freezing rain": "\\Hail",
                "light intensity shower rain": "\\faCloudRain",
                "shower rain": "\\faCloudRain",
                "heavy intensity shower rain": "\\faCloudRain",
                "ragged shower rain": "\\faCloudRain",
                "Snow": "\\faSnowflake",
                "Mist": "\\faSmog",
                "Smoke": "\\faSmog",
                "Haze": "\\faSmog",
                "Dust": "\\faSmog",
                "Fog": "\\faSmog",
                "Sand": "\\faSmog",
                "Ash": "\\faSmog",
                "Squall": "\\faSmog",
                "Tornado": "\\faSmog",
                "Clear": "\\faSun[regular]",
                "Clouds": "\\faCloud",
            },
        }
    )
)
