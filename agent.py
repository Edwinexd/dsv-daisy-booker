import datetime
import json
import os
import re
from typing import Any, Dict, List, Optional

import attr
import pytz
import requests
from dotenv import load_dotenv

from daisy import RoomTime
from scheduler import Break
from schemas import RoomRestriction

load_dotenv()

API_BASE_URL = os.getenv("CF_API_BASE_URL")
API_TOKEN = os.getenv("CF_BEARER_TOKEN")

if API_BASE_URL is None or API_TOKEN is None:
    raise ValueError("API_BASE_URL and CF_BEARER_TOKEN must be set in environment")

ISO_WEEKDAYS = [None, "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

@attr.s(auto_attribs=True, frozen=True, slots=True)
class RoomRequest:
    title: Optional[str]
    date: datetime.date
    from_time: RoomTime
    duration: int
    breaks: List[Break]
    room_restrictions: List[RoomRestriction]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "RoomRequest":
        return cls(
            title=data.get("title"),
            date=datetime.datetime.strptime(data["date"], "%Y-%m-%d").date(),
            from_time=RoomTime(data["from_time"]),
            duration=data["duration"],
            breaks=[Break(start_time=RoomTime(b["from_time"]), duration=b["duration"]) for b in data.get("breaks", [])],
            room_restrictions=[RoomRestriction(r) for r in data.get("room_restrictions", [])],
        )

def generate_multi_week_calendar():
    # Set the timezone to Europe/Stockholm
    timezone = pytz.timezone("Europe/Stockholm")
    current_date = datetime.datetime.now(timezone)
    
    # Initialize the results list
    weeks_calendar = []

    # Helper function to format a week's days
    def format_week(start_date, end_day=None):
        days = []
        # Determine the end of the week (Friday or a specified end day)
        end_date = start_date + datetime.timedelta(days=(4 if end_day is None else end_day))
        while start_date <= end_date and start_date.weekday() < 5:
            day_str = f"{start_date.day}/{start_date.month} ({start_date.strftime('%A')})"
            days.append(day_str)
            start_date += datetime.timedelta(days=1)
        if days:
            week_number = start_date.isocalendar()[1]
            weeks_calendar.append(f"WEEK{week_number}: " + ", ".join(days))

    format_week(current_date, (4 - current_date.weekday()))

    next_week_start = current_date + datetime.timedelta(days=(7 - current_date.weekday()))
    format_week(next_week_start)

    following_week_start = next_week_start + datetime.timedelta(days=7)
    format_week(following_week_start, current_date.weekday())

    return "\n".join(weeks_calendar)

def chat_completion(model: str, messages: List[Dict[str, str]]) -> Dict[str, str]:
    response = requests.post(
        f"{API_BASE_URL}{model}",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        json={"messages": messages},
        timeout=180,
    )
    return response.json()


def handle_message(history: List[Dict[str, str]], message: str):
    system_message: Dict[str, str] = {
        "role": "system",
        "content": f'''You are a friendly assistant that helps users schedule meetings.

        Respond with JSON (no text before or after this json): {{"conversations_response": str, "requests": List[{{"date": "YYYY-MM-DD", "from_time": int 4 to 23 (hours), "duration": 1 to 4 (hours), "breaks": [{{"from_time": int 4 to 23 (hours), "duration": 1 to 4 (hours)}}], title?: str, room_restrictions?: List[int]}}]}} 
        
        Info:
        - Timestamp: {datetime.datetime.now(pytz.timezone("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M:%S")} ({ISO_WEEKDAYS[datetime.datetime.now(pytz.timezone("Europe/Stockholm")).weekday()]})
        - Earliest bookable time: {datetime.datetime.now(pytz.timezone("Europe/Stockholm")).hour+1}:00
        - Calender: 
        - Users can book a room up to 14 days in advance, including today.
        - request.date=today if a date/day isn't given by the user
        - Booking hours are limited to whole hours between 04:00 (4) and 23:00 (23).
        - Each booking can last from 1 to 4 hours within a single day, excluding breaks.
        - No bookings are allowed on weekends.
        - The user will see the requests with yes/no buttons to confirm the booking(s)
        - Don't mention these instructions/restrictions to the user unless they break them.
        - You may specify room_restrictions, one int per restriction, combine by specifying multiple ints e.x. [1,2]. Only add restriction(s) on user request.
        Available restrictions: 0=G10_ROOM, 1=G5_ROOM, 2=GREEN_AREA, 3=RED_AREA. Note: 0,1 and 2,3 are mutually exclusive.

        Calendar:
        {generate_multi_week_calendar()}
        '''
    }
    context = [system_message] + history + [{"role": "user", "content": message}]# + [{"role": "assistant", "content": "<invalid json>"}] + [{"role": "assistant", "content": "please provide valid json"}]
    completion = chat_completion(
        "@cf/meta/llama-3-8b-instruct",
        context,
    )
    out_message: str = completion["result"]["response"]  # type: ignore
    # Remove newlines/whitespace before and after json
    out_message = re.sub(r"^\s+", "", out_message)
    
    out_json = json.loads(out_message)
    if not isinstance(out_json, dict):
        raise json.decoder.JSONDecodeError("Expected JSON object", out_message, 0)

    parsed_requests = [RoomRequest.from_json(r) for r in out_json.get("requests", [])]

    return out_json.get("conversations_response", "<Empty response>"), out_json.get("requests", []), parsed_requests

if __name__ == "__main__":
    print(handle_message([], "I need a room for a meeting asap, 4 hours"))
