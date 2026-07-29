from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class Event:
    event_id: str
    name: str
    date: str
    time: Optional[str]
    category: str
    event_type: str
    venue: str
    city: str
    state: str
    ticket_url: str
    weather: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        return asdict(self)