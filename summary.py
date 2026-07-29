from datetime import date, datetime, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo

from models import Event


CHICAGO_TIMEZONE = ZoneInfo("America/Chicago")


EVENT_ICONS = {
    "Cubs Game": "⚾",
    "Baseball": "⚾",
    "Concert": "🎵",
    "Football": "🏈",
    "College Football": "🏈",
    "Hockey": "🏒",
    "Soccer": "⚽",
    "Volleyball": "🏐",
}


def get_chicago_today() -> date:
    """
    Return the current calendar date in Chicago.
    """

    return datetime.now(
        CHICAGO_TIMEZONE
    ).date()


def get_summary_for_date(
    events: List[Event],
    target_date: date,
) -> str:
    """
    Generate a formatted summary for all events on a specific date.
    """

    matching_events = filter_events_by_date(
        events=events,
        target_date=target_date,
    )

    formatted_date = target_date.strftime(
        "%A, %B %d, %Y"
    ).replace(" 0", " ")

    lines = [
        "=" * 60,
        "Wrigley Field Daily Summary",
        formatted_date,
        "=" * 60,
        "",
    ]

    if not matching_events:
        lines.extend(
            [
                "No Wrigley Field events are currently scheduled.",
                "",
                "=" * 60,
            ]
        )

        return "\n".join(lines)

    event_word = (
        "event"
        if len(matching_events) == 1
        else "events"
    )

    lines.append(
        f"{len(matching_events)} {event_word} scheduled"
    )
    lines.append("")

    for index, event in enumerate(matching_events):
        lines.extend(format_event(event))

        if index < len(matching_events) - 1:
            lines.append("")
            lines.append("-" * 60)
            lines.append("")

    alerts = build_daily_alerts(matching_events)

    if alerts:
        lines.append("")
        lines.append("=" * 60)
        lines.append("Alerts")
        lines.append("=" * 60)
        lines.extend(alerts)

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def get_todays_summary(events: List[Event]) -> str:
    """
    Generate a summary for today's events in Chicago.
    """

    return get_summary_for_date(
        events=events,
        target_date=get_chicago_today(),
    )


def get_tomorrows_summary(events: List[Event]) -> str:
    """
    Generate a summary for tomorrow's events in Chicago.
    """

    return get_summary_for_date(
        events=events,
        target_date=(
            get_chicago_today()
            + timedelta(days=1)
        ),
    )


def filter_events_by_date(
    events: List[Event],
    target_date: date,
) -> List[Event]:
    """
    Return events matching the requested date, sorted by start time.
    """

    target_date_string = target_date.isoformat()

    matching_events = [
        event
        for event in events
        if event.date == target_date_string
    ]

    return sorted(
        matching_events,
        key=event_sort_key,
    )


def event_sort_key(event: Event) -> str:
    """
    Sort events by time, placing events without a listed time last.
    """

    return event.time or "99:99:99"


def format_event(event: Event) -> List[str]:
    """
    Format one event for a daily summary.
    """

    icon = EVENT_ICONS.get(
        event.event_type,
        "📍",
    )

    lines = [
        f"{icon} {event.name}",
        format_event_time(event.time),
        f"Event Type: {event.event_type}",
    ]

    if event.weather:
        lines.append("")
        lines.append("Weather")
        lines.append("-" * 20)

        temperature = event.weather.get(
            "temperature_f"
        )
        feels_like = event.weather.get(
            "feels_like_f"
        )
        condition = event.weather.get(
            "condition",
            "Unknown",
        )
        precipitation = event.weather.get(
            "precipitation_probability"
        )
        wind_speed = event.weather.get(
            "wind_speed_mph"
        )

        if temperature is not None:
            lines.append(
                "Temperature: "
                f"{format_number(temperature)}°F"
            )

        if feels_like is not None:
            lines.append(
                "Feels Like: "
                f"{format_number(feels_like)}°F"
            )

        lines.append(
            f"Conditions: {condition}"
        )

        if precipitation is not None:
            lines.append(
                "Rain Chance: "
                f"{format_number(precipitation)}%"
            )

        if wind_speed is not None:
            lines.append(
                "Wind: "
                f"{format_number(wind_speed)} mph"
            )
    else:
        lines.append("")
        lines.append(
            "Weather: Forecast not yet available"
        )

    if event.ticket_url:
        lines.append("")
        lines.append(
            f"Tickets: {event.ticket_url}"
        )

    return lines


def build_daily_alerts(
    events: List[Event],
) -> List[str]:
    """
    Generate crowd and weather alerts for a day's events.
    """

    alerts = []

    if len(events) >= 2:
        alerts.append(
            "⚠ Busy day: Multiple events are scheduled near "
            "Wrigley Field."
        )

    highest_rain_chance = get_highest_weather_value(
        events=events,
        field_name="precipitation_probability",
    )

    if (
        highest_rain_chance is not None
        and highest_rain_chance >= 50
    ):
        alerts.append(
            "🌧 Rain likely: At least one event has a "
            f"{format_number(highest_rain_chance)}% chance "
            "of precipitation."
        )

    highest_temperature = get_highest_weather_value(
        events=events,
        field_name="temperature_f",
    )

    if (
        highest_temperature is not None
        and highest_temperature >= 90
    ):
        alerts.append(
            "🔥 Hot weather: Temperatures may reach "
            f"{format_number(highest_temperature)}°F."
        )

    strongest_wind = get_highest_weather_value(
        events=events,
        field_name="wind_speed_mph",
    )

    if (
        strongest_wind is not None
        and strongest_wind >= 20
    ):
        alerts.append(
            "💨 Strong winds: Forecast wind speeds may reach "
            f"{format_number(strongest_wind)} mph."
        )

    return alerts


def get_highest_weather_value(
    events: List[Event],
    field_name: str,
) -> Optional[float]:
    """
    Return the highest numeric weather value for the supplied field.
    """

    values = []

    for event in events:
        if not event.weather:
            continue

        value = event.weather.get(
            field_name
        )

        if isinstance(
            value,
            (int, float),
        ):
            values.append(
                float(value)
            )

    if not values:
        return None

    return max(values)


def format_event_time(
    event_time: Optional[str],
) -> str:
    """
    Convert a 24-hour Ticketmaster time into a readable time.
    """

    if not event_time:
        return "Time not listed"

    supported_formats = [
        "%H:%M:%S",
        "%H:%M",
    ]

    for time_format in supported_formats:
        try:
            parsed_time = datetime.strptime(
                event_time,
                time_format,
            )

            return parsed_time.strftime(
                "%I:%M %p"
            ).lstrip("0")
        except ValueError:
            continue

    return event_time


def format_number(
    value: float,
) -> str:
    """
    Display whole numbers without decimals while preserving useful
    decimal values.
    """

    numeric_value = float(value)

    if numeric_value.is_integer():
        return str(
            int(numeric_value)
        )

    return f"{numeric_value:.1f}"