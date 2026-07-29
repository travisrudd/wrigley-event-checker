import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


SUMMARY_FILE = Path("output/daily_summary.txt")


def format_whatsapp_number(phone_number: str) -> str:
    cleaned_number = phone_number.strip()

    if cleaned_number.startswith("whatsapp:"):
        return cleaned_number

    return "whatsapp:{}".format(cleaned_number)


def read_daily_summary() -> str:
    if not SUMMARY_FILE.exists():
        raise FileNotFoundError(
            "Daily summary was not found at {}".format(SUMMARY_FILE)
        )

    summary = SUMMARY_FILE.read_text(encoding="utf-8").strip()

    if not summary:
        raise ValueError("The daily summary file is empty.")

    return summary


def send_whatsapp_message(
    message_body: str,
    account_sid: Optional[str] = None,
    auth_token: Optional[str] = None,
    from_number: Optional[str] = None,
    to_number: Optional[str] = None,
) -> str:
    account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
    from_number = from_number or os.getenv("TWILIO_WHATSAPP_FROM")
    to_number = to_number or os.getenv("TWILIO_WHATSAPP_TO")

    missing_variables = []

    if not account_sid:
        missing_variables.append("TWILIO_ACCOUNT_SID")

    if not auth_token:
        missing_variables.append("TWILIO_AUTH_TOKEN")

    if not from_number:
        missing_variables.append("TWILIO_WHATSAPP_FROM")

    if not to_number:
        missing_variables.append("TWILIO_WHATSAPP_TO")

    if missing_variables:
        raise ValueError(
            "Missing required environment variables: {}".format(
                ", ".join(missing_variables)
            )
        )

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message_body,
        from_=format_whatsapp_number(from_number),
        to=format_whatsapp_number(to_number),
    )

    return message.sid


def main() -> None:
    load_dotenv()

    try:
        summary = read_daily_summary()
        message_sid = send_whatsapp_message(summary)

        print("WhatsApp message submitted successfully.")
        print("Message SID: {}".format(message_sid))

    except FileNotFoundError as error:
        print("WhatsApp message was not sent: {}".format(error))
        sys.exit(1)

    except ValueError as error:
        print("WhatsApp configuration error: {}".format(error))
        sys.exit(1)

    except TwilioRestException as error:
        print("Twilio rejected the WhatsApp message.")
        print("Error code: {}".format(error.code))
        print("Error message: {}".format(error.msg))
        sys.exit(1)

    except Exception as error:
        print("Unexpected WhatsApp error: {}".format(error))
        sys.exit(1)


if __name__ == "__main__":
    main()