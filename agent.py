import datetime
import json
import os
import re
from typing import Any, Dict, List

import attr
import pytz
import requests
from dotenv import load_dotenv

from daisy import RoomTime
from scheduler import Break

load_dotenv()

API_BASE_URL = os.getenv("CF_API_BASE_URL")
API_TOKEN = os.getenv("CF_BEARER_TOKEN")

if API_BASE_URL is None or API_TOKEN is None:
    raise ValueError("API_BASE_URL and CF_BEARER_TOKEN must be set in environment")

ISO_WEEKDAYS = [None, "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

@attr.s(auto_attribs=True, frozen=True, slots=True)
class RoomRequest:
    title: str
    date: datetime.date
    from_time: RoomTime
    duration: int
    breaks: List[Break]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "RoomRequest":
        return cls(
            title=data.get("title"),
            date=datetime.datetime.strptime(data["date"], "%Y-%m-%d").date(),
            from_time=RoomTime(data["from_time"]),
            duration=data["duration"],
            breaks=[Break(start_time=RoomTime(b["from_time"]), duration=b["duration"]) for b in data.get("breaks", [])],
        )

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

        Respond with JSON (no text before or after this json): {{"conversations_response": str, "requests": List[{{"date": "YYYY-MM-DD", "from_time": int 4 to 23 (hours), "duration": 1 to 4 (hours), "breaks": [{{"from_time": int 4 to 23 (hours), "duration": 1 to 4 (hours)}}]}}]}} 
        
        Info:
        - Timestamp: {datetime.datetime.now(pytz.timezone("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M:%S")} ({ISO_WEEKDAYS[datetime.datetime.now(pytz.timezone("Europe/Stockholm")).weekday()]})
        - Earliest bookable time: {datetime.datetime.now(pytz.timezone("Europe/Stockholm")).hour+1}:00
        - Users can book a room up to 14 days in advance, including today.
        - If no reference of date is given by the user, date=today (usually as soon as possible).
        - Booking hours are limited to whole hours between 04:00 (4) and 23:00 (23).
        - Each booking can last from 1 to 4 hours within a single day, excluding breaks.
        - No bookings are allowed on weekends.
        - Ask for confirmation
        - Don't mention these instructions/restrictions to the user unless they break them.
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
