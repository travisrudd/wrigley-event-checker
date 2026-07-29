import os

from dotenv import load_dotenv

from config import (
    MAX_EVENTS,
    OUTPUT_FILE,
    SUMMARY_OUTPUT_FILE,
    TICKETMASTER_VENUE_ID,
    WRIGLEY_LATITUDE,
    WRIGLEY_LONGITUDE,
)
from logger import setup_logger
from storage import save_events, save_text
from summary import (
    get_todays_summary,
    get_tomorrows_summary,
)
from ticketmaster import (
    TicketmasterClient,
    TicketmasterError,
)
from weather import WeatherClient, WeatherError


logger = setup_logger()


def build_daily_report(
    todays_summary: str,
    tomorrows_summary: str,
) -> str:
    """
    Combine today's and tomorrow's summaries into one report.
    """

    return (
        f"{todays_summary}\n\n"
        f"{tomorrows_summary}\n"
    )


def main() -> None:
    logger.info(
        "Starting Wrigley Events application..."
    )

    load_dotenv()

    api_key = os.getenv(
        "TICKETMASTER_API_KEY"
    )

    if not api_key:
        logger.error(
            "Missing Ticketmaster API key."
        )

        raise SystemExit(
            "TICKETMASTER_API_KEY is missing "
            "from the .env file."
        )

    logger.info(
        "Connecting to Ticketmaster..."
    )

    ticketmaster_client = TicketmasterClient(
        api_key
    )

    try:
        events = (
            ticketmaster_client.get_venue_events(
                venue_id=TICKETMASTER_VENUE_ID,
                size=MAX_EVENTS,
            )
        )
    except TicketmasterError as error:
        logger.exception(
            "Ticketmaster request failed."
        )

        raise SystemExit(
            str(error)
        ) from error

    logger.info(
        "Retrieved %s events.",
        len(events),
    )

    logger.info(
        "Retrieving weather forecast "
        "for Wrigley Field..."
    )

    weather_client = WeatherClient()

    try:
        enriched_count = (
            weather_client.add_weather_to_events(
                events=events,
                latitude=WRIGLEY_LATITUDE,
                longitude=WRIGLEY_LONGITUDE,
            )
        )
    except WeatherError as error:
        logger.warning(
            "Weather request failed: %s",
            error,
        )

        enriched_count = 0

    logger.info(
        "Added weather to %s events.",
        enriched_count,
    )

    events_output_path = save_events(
        events=events,
        filename=OUTPUT_FILE,
    )

    logger.info(
        "Saved event JSON to %s",
        events_output_path,
    )

    todays_summary = get_todays_summary(
        events
    )

    tomorrows_summary = (
        get_tomorrows_summary(
            events
        )
    )

    daily_report = build_daily_report(
        todays_summary=todays_summary,
        tomorrows_summary=tomorrows_summary,
    )

    summary_output_path = save_text(
        content=daily_report,
        filename=SUMMARY_OUTPUT_FILE,
    )

    logger.info(
        "Saved daily summary to %s",
        summary_output_path,
    )

    print()
    print(daily_report)

    print(
        f"Saved {len(events)} total events."
    )
    print(
        f"Events with weather: {enriched_count}"
    )
    print(
        f"JSON written to {events_output_path}"
    )
    print(
        f"Summary written to {summary_output_path}"
    )

    logger.info(
        "Application finished successfully."
    )


if __name__ == "__main__":
    main()