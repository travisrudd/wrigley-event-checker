from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from models import Event


class WeatherError(Exception):
    """Raised when an Open-Meteo weather request fails."""


class WeatherClient:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    WEATHER_DESCRIPTIONS = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Freezing fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Heavy drizzle",
        56: "Light freezing drizzle",
        57: "Heavy freezing drizzle",
        61: "Light rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Light snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Light rain showers",
        81: "Moderate rain showers",
        82: "Heavy rain showers",
        85: "Light snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with light hail",
        99: "Thunderstorm with heavy hail",
    }

    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout

    def get_hourly_forecast(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        """
        Retrieve the hourly forecast for the supplied coordinates.
        """

        response = requests.get(
            self.BASE_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "hourly": (
                    "temperature_2m,"
                    "apparent_temperature,"
                    "precipitation_probability,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "precipitation_unit": "inch",
                "timezone": "America/Chicago",
                "forecast_days": 16,
            },
            timeout=self.timeout,
        )

        if not response.ok:
            raise WeatherError(
                f"Open-Meteo returned status "
                f"{response.status_code}: {response.text}"
            )

        return response.json()

    def add_weather_to_events(
        self,
        events: List[Event],
        latitude: float,
        longitude: float,
    ) -> int:
        """
        Add an hourly weather forecast to events that fall within
        the available forecast period.

        Returns the number of events that received weather data.
        """

        forecast = self.get_hourly_forecast(
            latitude=latitude,
            longitude=longitude,
        )

        hourly = forecast.get("hourly", {})
        forecast_lookup = self._build_forecast_lookup(hourly)

        enriched_count = 0

        for event in events:
            event.weather = self._forecast_for_event(
                event=event,
                forecast_lookup=forecast_lookup,
            )

            if event.weather is not None:
                enriched_count += 1

        return enriched_count

    def _build_forecast_lookup(
        self,
        hourly: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Convert Open-Meteo's parallel hourly lists into a dictionary
        keyed by date and hour.
        """

        times = hourly.get("time", [])
        temperatures = hourly.get("temperature_2m", [])
        apparent_temperatures = hourly.get(
            "apparent_temperature",
            [],
        )
        precipitation_probabilities = hourly.get(
            "precipitation_probability",
            [],
        )
        weather_codes = hourly.get("weather_code", [])
        wind_speeds = hourly.get("wind_speed_10m", [])

        lookup = {}

        for index, forecast_time in enumerate(times):
            weather_code = self._value_at(
                weather_codes,
                index,
            )

            lookup[forecast_time] = {
                "forecast_time": forecast_time,
                "temperature_f": self._value_at(
                    temperatures,
                    index,
                ),
                "feels_like_f": self._value_at(
                    apparent_temperatures,
                    index,
                ),
                "precipitation_probability": self._value_at(
                    precipitation_probabilities,
                    index,
                ),
                "weather_code": weather_code,
                "condition": self.WEATHER_DESCRIPTIONS.get(
                    weather_code,
                    "Unknown",
                ),
                "wind_speed_mph": self._value_at(
                    wind_speeds,
                    index,
                ),
            }

        return lookup

    def _forecast_for_event(
        self,
        event: Event,
        forecast_lookup: Dict[str, Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Find the forecast hour closest to the event's start time.
        """

        if event.date == "Unknown date":
            return None

        event_time = event.time or "12:00:00"

        try:
            event_datetime = datetime.strptime(
                f"{event.date} {event_time}",
                "%Y-%m-%d %H:%M:%S",
            )
        except ValueError:
            return None

        rounded_datetime = event_datetime.replace(
            minute=0,
            second=0,
            microsecond=0,
        )

        if event_datetime.minute >= 30:
            rounded_datetime += timedelta(hours=1)

        lookup_key = rounded_datetime.strftime(
            "%Y-%m-%dT%H:00"
        )

        return forecast_lookup.get(lookup_key)

    @staticmethod
    def _value_at(
        values: List[Any],
        index: int,
    ) -> Any:
        """
        Safely retrieve an item from an Open-Meteo hourly list.
        """

        if index >= len(values):
            return None

        return values[index]