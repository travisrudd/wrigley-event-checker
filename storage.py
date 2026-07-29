import json
import os
from typing import List

from models import Event


def save_events(
    events: List[Event],
    filename: str,
) -> str:
    """
    Save a list of Event objects as formatted JSON.

    Returns the path of the saved file.
    """

    ensure_parent_folder_exists(filename)

    event_data = [
        event.to_dict()
        for event in events
    ]

    with open(
        filename,
        "w",
        encoding="utf-8",
    ) as output_file:
        json.dump(
            event_data,
            output_file,
            indent=4,
            ensure_ascii=False,
        )

    return filename


def save_text(
    content: str,
    filename: str,
) -> str:
    """
    Save plain-text content to a file.

    Returns the path of the saved file.
    """

    ensure_parent_folder_exists(filename)

    with open(
        filename,
        "w",
        encoding="utf-8",
    ) as output_file:
        output_file.write(content)

        if not content.endswith("\n"):
            output_file.write("\n")

    return filename


def ensure_parent_folder_exists(
    filename: str,
) -> None:
    """
    Create the file's parent folder when it does not exist.
    """

    parent_folder = os.path.dirname(filename)

    if parent_folder:
        os.makedirs(
            parent_folder,
            exist_ok=True,
        )