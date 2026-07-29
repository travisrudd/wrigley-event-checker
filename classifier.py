def classify_event(event_name: str, ticketmaster_category: str) -> str:
    """
    Return a more useful event type based on the event name.

    The Ticketmaster category is used as a fallback when no specific
    event type can be identified.
    """

    name = event_name.lower()

    if "chicago cubs" in name:
        return "Cubs Game"

    if "volleyball" in name:
        return "Volleyball"

    if "football" in name:
        if any(
            college_name in name
            for college_name in (
                "northwestern",
                "illinois",
                "notre dame",
                "big ten",
                "big 10",
                "sec",
            )
        ):
            return "College Football"

        return "Football"

    if any(
        hockey_term in name
        for hockey_term in (
            "hockey",
            "winter classic",
            "blackhawks",
            "nhl",
        )
    ):
        return "Hockey"

    if any(
        soccer_term in name
        for soccer_term in (
            "soccer",
            "chicago fire",
            "mls",
        )
    ):
        return "Soccer"

    if any(
        concert_term in name
        for concert_term in (
            "concert",
            "tour",
            "live in concert",
        )
    ):
        return "Concert"

    if ticketmaster_category:
        return ticketmaster_category

    return "Other"