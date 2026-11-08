
import os
import json
import re
import subprocess
from datetime import datetime, timedelta
import zoneinfo

JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meeting_assistant.json")
SRI_LANKA_TZ = zoneinfo.ZoneInfo("Asia/Colombo")


def default_data():
    return {"aliases": {}, "meetings": {}}


def load_data():
    if not os.path.exists(JSON_PATH):
        return default_data()

    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return default_data()

        data.setdefault("aliases", {})
        data.setdefault("meetings", {})
        return data

    except (json.JSONDecodeError, OSError):
        return default_data()


def save_data(data):
    temp_path = JSON_PATH + ".tmp"

    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    os.replace(temp_path, JSON_PATH)


# --- Group Alias Management ---

def add_alias(group_name: str, alias: str) -> str:
    group_name = group_name.strip()
    alias = alias.strip()

    if not group_name or not alias:
        return "Please provide both a group name and an alias."

    data = load_data()
    data["aliases"][alias.lower()] = group_name
    save_data(data)

    return f"I've remembered '{group_name}' as '{alias}'."


def get_group_from_alias(alias: str) -> str:
    data = load_data()
    return data["aliases"].get(alias.strip().lower(), alias)


def list_aliases() -> dict:
    return load_data().get("aliases", {})


def remove_alias(alias: str) -> str:
    data = load_data()
    key = alias.strip().lower()

    if key in data["aliases"]:
        del data["aliases"][key]
        save_data(data)
        return f"I've removed the alias '{alias}'."

    return f"I couldn't find any group alias named '{alias}'."


# --- Zoom Link Detection ---

def extract_zoom_details(message_text: str):
    """
    Detect common Zoom meeting URLs, including regional Zoom subdomains.
    """
    if not message_text:
        return None

    zoom_regex = (
        r"https?://"
        r"(?:[A-Za-z0-9-]+\.)*zoom\.us/"
        r"(?:j|s)/"
        r"[A-Za-z0-9?=&_%\-]+"
    )

    match = re.search(zoom_regex, message_text, re.IGNORECASE)

    if not match:
        return None

    # Remove common punctuation accidentally attached to the URL.
    return match.group(0).rstrip(".,;!)]}")


# --- Date and Time Processing ---

def parse_relative_time(message_text: str):
    """
    Extract a time such as 5:30 PM or 17:30.
    If the message contains no recognizable time, return None.

    This function does not guess the meeting date from phrases such as
    'tomorrow' or 'next Monday'.
    """
    if not message_text:
        return None

    now = datetime.now(SRI_LANKA_TZ)
    text = message_text.lower()

    time_match = re.search(
        r"\b(\d{1,2})[:.](\d{2})\s*(am|pm)?\b",
        text,
        re.IGNORECASE
    )

    if not time_match:
        return None

    hour = int(time_match.group(1))
    minute = int(time_match.group(2))
    ampm = time_match.group(3)

    if minute > 59:
        return None

    if ampm:
        if not 1 <= hour <= 12:
            return None

        if ampm.lower() == "pm" and hour < 12:
            hour += 12
        elif ampm.lower() == "am" and hour == 12:
            hour = 0
    elif not 0 <= hour <= 23:
        return None

    target_date = now.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    # Respect explicit relative-day wording instead of silently moving a
    # past time stated for "today" into tomorrow.
    if re.search(r"\btomorrow\b", text, re.IGNORECASE):
        target_date += timedelta(days=1)
    elif re.search(r"\btoday\b", text, re.IGNORECASE):
        pass
    elif target_date < now:
        # With no date stated, retain the existing next-occurrence behaviour.
        target_date += timedelta(days=1)

    return target_date


# --- macOS Calendar Integration ---

def _applescript_string(value: str) -> str:
    """Safely quote a string for AppleScript."""
    value = str(value).replace("\\", "\\\\").replace('"', '\\"')
    value = value.replace("\n", " ").replace("\r", " ")
    return f'"{value}"'


def _date_applescript(variable: str, dt: datetime) -> str:
    """Build AppleScript that sets a date using numeric components."""
    dt = dt.astimezone(SRI_LANKA_TZ)

    month_names = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ]

    month_name = month_names[dt.month - 1]

    return f"""
    set {variable} to current date
    set year of {variable} to {dt.year}
    set month of {variable} to {month_name}
    set day of {variable} to {dt.day}
    set hours of {variable} to {dt.hour}
    set minutes of {variable} to {dt.minute}
    set seconds of {variable} to 0
    """


def add_to_macos_calendar(
    title: str,
    url: str,
    start_time: datetime,
    duration_mins: int = 60,
    meeting_id: str = ""
) -> bool:

    global _LAST_MEETING_ACTION_ERROR
    if duration_mins <= 0:
        _LAST_MEETING_ACTION_ERROR = "Meeting duration must be greater than zero."
        return False

    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=SRI_LANKA_TZ)

    start_time = start_time.astimezone(SRI_LANKA_TZ)
    end_time = start_time + timedelta(minutes=duration_mins)

    marker = f"E.V. meeting id: {meeting_id}" if meeting_id else "Scheduled by E.V."
    script = f"""
    tell application "Calendar"
        set targetCalendar to first calendar
        try
            set targetCalendar to calendar "Work"
        end try
        {_date_applescript("startDate", start_time)}
        {_date_applescript("endDate", end_time)}
        set markerText to {_applescript_string(marker)}
        set alreadyThere to false
        try
            repeat with existingEvent in (every event of targetCalendar)
                try
                    if (description of existingEvent as text) contains markerText then
                        set alreadyThere to true
                        exit repeat
                    end if
                end try
            end repeat
        end try
        if not alreadyThere then
            tell targetCalendar
                make new event at end of events with properties {{
                    summary:{_applescript_string(title)},
                    start date:startDate,
                    end date:endDate,
                    url:{_applescript_string(url)},
                    description:markerText
                }}
            end tell
        end if
    end tell
    """

    try:
        subprocess.run(
            ["osascript", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            timeout=20
        )
        _LAST_MEETING_ACTION_ERROR = ""
        return True

    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or str(exc)).strip()
        _LAST_MEETING_ACTION_ERROR = (
            "macOS Calendar could not create the event. "
            + (detail[:700] if detail else "osascript returned an error.")
        )
        return False
    except subprocess.TimeoutExpired:
        _LAST_MEETING_ACTION_ERROR = "macOS Calendar did not respond within 20 seconds."
        return False
    except OSError as exc:
        _LAST_MEETING_ACTION_ERROR = f"Could not run osascript: {exc}"
        return False


def open_zoom_link(url: str) -> bool:
    if not extract_zoom_details(url):
        return False

    try:
        subprocess.run(
            ["open", url],
            check=True,
            capture_output=True,
            text=True,
            timeout=15
        )
        return True

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return False


# Last approval/action failure, exposed to server.py for useful API errors.
_LAST_MEETING_ACTION_ERROR = ""

def get_last_meeting_action_error() -> str:
    """Return the reason the most recent meeting action failed, if any."""
    return _LAST_MEETING_ACTION_ERROR


# --- Scheduling Workflow ---

def register_pending_meeting(
    msg_id: str,
    group: str,
    sender: str,
    url: str,
    text: str
):
    data = load_data()

    if msg_id in data["meetings"]:
        return None

    if not extract_zoom_details(url):
        return None

    parsed_time = parse_relative_time(text)

    # Store the meeting as pending. Detection never means approval.
    data["meetings"][msg_id] = {
        "group": group,
        "sender": sender,
        "url": url,
        "text": text,
        "status": "pending",
        "scheduled_time": parsed_time.isoformat() if parsed_time else None,
        "duration": 60,
        "opened": False
    }

    save_data(data)

    # Alias is stored as alias -> original group name.
    alias_dict = {
        group_name.lower(): alias
        for alias, group_name in data["aliases"].items()
    }

    display_name = alias_dict.get(group.lower(), group)

    return {
        "msg_id": msg_id,
        "group": group,
        "display_name": display_name,
        "sender": sender,
        "url": url,
        "message": text,
        "scheduled_time": parsed_time.isoformat() if parsed_time else None,
        "time_str": (
            parsed_time.strftime("%I:%M %p")
            if parsed_time else "Unspecified Time"
        ),
        "status": "pending",
    }


def update_meeting_status(
    msg_id: str,
    status: str,
    explicit_time_iso: str = None
) -> bool:
    global _LAST_MEETING_ACTION_ERROR
    _LAST_MEETING_ACTION_ERROR = ""

    allowed_statuses = {"pending", "approved", "ignored", "cancelled"}
    if status not in allowed_statuses:
        _LAST_MEETING_ACTION_ERROR = f"Unsupported meeting action: {status!r}."
        return False

    data = load_data()
    if msg_id not in data.get("meetings", {}):
        _LAST_MEETING_ACTION_ERROR = "Meeting was not found. It may have expired or already been removed."
        return False

    meeting = data["meetings"][msg_id]

    if explicit_time_iso:
        try:
            parsed = datetime.fromisoformat(explicit_time_iso)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=SRI_LANKA_TZ)
            meeting["scheduled_time"] = parsed.isoformat()
        except (TypeError, ValueError) as exc:
            _LAST_MEETING_ACTION_ERROR = f"Invalid meeting date/time: {exc}"
            return False

    if status == "approved":
        if not meeting.get("scheduled_time"):
            _LAST_MEETING_ACTION_ERROR = (
                "Meeting time is missing. Please set a date and time before approving."
            )
            return False

        try:
            start_time = datetime.fromisoformat(meeting["scheduled_time"])
        except (TypeError, ValueError) as exc:
            _LAST_MEETING_ACTION_ERROR = f"Stored meeting date/time is invalid: {exc}"
            return False

        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=SRI_LANKA_TZ)

        if not meeting.get("calendar_event_created"):
            calendar_created = add_to_macos_calendar(
                title=f"Zoom: {meeting.get('group', 'WhatsApp')} via {meeting.get('sender', 'Unknown sender')}",
                url=meeting.get("url", ""),
                start_time=start_time,
                duration_mins=meeting.get("duration", 60),
                meeting_id=msg_id
            )
            if not calendar_created:
                if not _LAST_MEETING_ACTION_ERROR:
                    _LAST_MEETING_ACTION_ERROR = (
                        "macOS Calendar did not confirm event creation. "
                        "Check Calendar automation permissions."
                    )
                return False
            meeting["calendar_event_created"] = True

    meeting["status"] = status
    save_data(data)
    _LAST_MEETING_ACTION_ERROR = ""
    return True


def get_meetings_for_alias(alias: str):
    """Return meetings whose original WhatsApp group matches an alias or group name."""
    wanted = get_group_from_alias(alias).strip().casefold()
    data = load_data()
    matches = []
    for meeting_id, meeting in data.get("meetings", {}).items():
        group = str(meeting.get("group", "")).strip()
        if group.casefold() == wanted or group.casefold() == alias.strip().casefold():
            matches.append({"msg_id": meeting_id, **meeting})
    matches.sort(key=lambda item: item.get("scheduled_time") or "")
    return matches


def mark_meeting_opened(msg_id: str) -> bool:
    """Persist the auto-open guard without re-running approval/calendar creation."""
    data = load_data()
    meeting = data.get("meetings", {}).get(msg_id)
    if not meeting or meeting.get("status") != "approved":
        return False
    if meeting.get("opened"):
        return True
    meeting["opened"] = True
    save_data(data)
    return True


# --- Natural Language Commands ---

def execute_natural_command(command_text: str) -> str:
    original_cmd = command_text.strip()
    cmd = original_cmd.lower()

    data = load_data()
    now = datetime.now(SRI_LANKA_TZ)

    # 1. Remember a group alias.
    remember_match = re.search(
        r"remember\s+(.+?)\s+as\s+(.+)",
        original_cmd,
        re.IGNORECASE
    )

    if remember_match:
        return add_alias(
            remember_match.group(1).strip(),
            remember_match.group(2).strip()
        )

    # 2. List saved aliases.
    if "show my saved group names" in cmd:
        aliases = list_aliases()

        if not aliases:
            return "You haven't saved any group aliases yet."

        return "Here are your saved groups:\n" + "\n".join(
            f"• {alias.title()} -> {group}"
            for alias, group in aliases.items()
        )

    # 3. Remove an alias.
    remove_match = re.search(
        r"(?:remove|delete|forget)\s+(?:the\s+)?(?:group\s+)?alias\s+(.+)",
        original_cmd,
        re.IGNORECASE
    )

    if remove_match:
        return remove_alias(remove_match.group(1).strip())

    # 4. Answer singular/plural natural-language questions about today's meetings.
    # Match this before the LLM so it cannot invent a person or meeting time.
    asks_about_today = (
        re.search(r"\bmeetings?\s+(?:scheduled\s+)?today\b", cmd)
        or re.search(r"\b(?:today'?s)\s+meetings?\b", cmd)
        or re.search(r"\bdo\s+i\s+have\s+(?:a\s+)?meeting\s+today\b", cmd)
    )
    if asks_about_today:
        todays_meetings = []

        for meeting_id, meeting in data["meetings"].items():
            # Only approved meetings are confirmed calendar commitments.
            if meeting.get("status") != "approved":
                continue

            scheduled_time = meeting.get("scheduled_time")
            if not scheduled_time:
                continue

            try:
                meeting_time = datetime.fromisoformat(scheduled_time)
                if meeting_time.tzinfo is None:
                    meeting_time = meeting_time.replace(tzinfo=SRI_LANKA_TZ)
                meeting_time = meeting_time.astimezone(SRI_LANKA_TZ)
                if meeting_time.date() == now.date():
                    todays_meetings.append((meeting_time, meeting_id, meeting))
            except (TypeError, ValueError):
                continue

        todays_meetings.sort(key=lambda item: item[0])
        if not todays_meetings:
            return "You have no approved Zoom meetings scheduled for today."

        lines = [f"You have {len(todays_meetings)} approved Zoom meeting(s) today:"]
        for meeting_time, meeting_id, meeting in todays_meetings:
            group = meeting.get("group") or "Unknown WhatsApp group"
            sender = meeting.get("sender") or "Unknown sender"
            lines.append(
                f"• {meeting_time.strftime('%I:%M %p')} — {group} — {sender}"
            )
        return "\n".join(lines)

    # 5. Cancel the next approved Zoom meeting.
    if "cancel my next zoom meeting" in cmd:
        upcoming = []

        for meeting_id, meeting in data["meetings"].items():
            if meeting.get("status") != "approved":
                continue

            scheduled_time = meeting.get("scheduled_time")

            if not scheduled_time:
                continue

            try:
                meeting_time = datetime.fromisoformat(scheduled_time)

                if meeting_time.tzinfo is None:
                    meeting_time = meeting_time.replace(
                        tzinfo=SRI_LANKA_TZ
                    )

                if meeting_time > now:
                    upcoming.append((meeting_time, meeting_id))

            except ValueError:
                continue

        if not upcoming:
            return "There are no upcoming active Zoom meetings scheduled."

        upcoming.sort(key=lambda item: item[0])
        next_id = upcoming[0][1]

        if update_meeting_status(next_id, "cancelled"):
            return "I've cancelled your next scheduled Zoom meeting."

        return "I couldn't cancel the meeting. Please try again."

    # Ask about meetings from a named group or saved alias (e.g. "meetings from CK Sir").
    source_match = re.search(r"(?:meetings?|zoom meetings?)\s+(?:from|in)\s+(.+?)(?:[?.!]|$)", original_cmd, re.IGNORECASE)
    if source_match:
        label = source_match.group(1).strip()
        matches = [m for m in get_meetings_for_alias(label) if m.get("status") in ("pending", "approved")]
        if not matches:
            return f"I couldn't find any pending or approved Zoom meetings from {label}."
        lines = []
        for item in matches:
            when = item.get("scheduled_time") or "time not specified"
            lines.append(f"{item.get('status', 'pending').title()}: {when} — {item.get('group', label)} ({item.get('sender', 'unknown sender')})")
        return "Here are the Zoom meetings from " + label + ":\n" + "\n".join(lines)

    return "Command recognized, but no matching workflow action was found."
