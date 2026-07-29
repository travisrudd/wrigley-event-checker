from typing import Any, List

import requests

from classifier import classify_event
from models import Event


class TicketmasterError(Exception):
    """Raised when a Ticketmaster API request fails."""


class TicketmasterClient:
    BASE_URL = "https://app.ticketmaster.com/discovery/v2"

    def __init__(self, api_key: str, timeout: int = 30) -> None:
        if not api_key:
            raise ValueError("A Ticketmaster API key is required.")

        self.api_key = api_key
        self.timeout = timeout

    def get_venue_events(
        self,
        venue_id: str,
        size: int = 100,
    ) -> List[Event]:
        response = requests.get(
            f"{self.BASE_URL}/events.json",
            params={
                "apikey": self.api_key,
                "venueId": venue_id,
                "countryCode": "US",
                "sort": "date,asc",
                "size": size,
            },
            timeout=self.timeout,
        )

        if not response.ok:
            raise TicketmasterError(
                f"Ticketmaster returned status "
                f"{response.status_code}: {response.text}"
            )

        data = response.json()
        raw_events = data.get("_embedded", {}).get("events", [])

        return [self._parse_event(event) for event in raw_events]

    @staticmethod
    def _parse_event(data: dict) -> Event:
        start = data.get("dates", {}).get("start", {})

        classifications = data.get("classifications", [])
        classification = classifications[0] if classifications else {}

        category = classification.get(
            "segment",
            {},
        ).get("name", "Unclassified")

        event_name = data.get("name", "Unnamed event")

        venues = data.get("_embedded", {}).get("venues", [])
        venue = venues[0] if venues else {}

        return Event(
            event_id=data.get("id", ""),
            name=event_name,
            date=start.get("localDate", "Unknown date"),
            time=start.get("localTime"),
            category=category,
            event_type=classify_event(
                event_name=event_name,
                ticketmaster_category=category,
            ),
            venue=venue.get("name", "Unknown venue"),
            city=venue.get("city", {}).get(
                "name",
                "Unknown city",
            ),
            state=venue.get("state", {}).get(
                "stateCode",
                "",
            ),
            ticket_url=data.get("url", ""),
        )