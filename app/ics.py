from datetime import datetime
import uuid


def generate_ics(
    event_title: str,
    event_description: str,
    event_location: str,
    start_time: datetime,
    end_time: datetime,
    uid: str = None,
) -> str:
    if uid is None:
        uid = str(uuid.uuid4())

    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dtstart = start_time.strftime("%Y%m%dT%H%M%SZ")
    dtend = end_time.strftime("%Y%m%dT%H%M%SZ")

    ics_content = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "PRODID:-//PAW CONNEct//Paw Connect//EN\n"
        "BEGIN:VEVENT\n"
        f"UID:{uid}\n"
        f"DTSTAMP:{dtstamp}\n"
        f"DTSTART:{dtstart}\n"
        f"DTEND:{dtend}\n"
        f"SUMMARY:{event_title}\n"
        f"DESCRIPTION:{event_description}\n"
        f"LOCATION:{event_location}\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n"
    )
    return ics_content
