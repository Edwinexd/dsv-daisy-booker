import datetime
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

import attr
import pytz
import requests
from dotenv import load_dotenv

from daisy import RoomTime
from scheduler import Break
from schemas import RoomCategory, RoomRestriction

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
    room_category: RoomCategory

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "RoomRequest":
        return cls(
            title=data.get("title"),
            date=datetime.datetime.strptime(data["date"], "%Y-%m-%d").date(),
            from_time=RoomTime(data["from_time"]),
            duration=data["duration"],
            breaks=[Break(start_time=RoomTime(b["from_time"]), duration=b["duration"]) for b in data.get("breaks", [])],
            room_restrictions=[RoomRestriction(r) for r in data.get("room_filters", [])],
            room_category=RoomCategory(int(data.get("room_category", RoomCategory.BOOKABLE_GROUP_ROOMS.value)) if data.get("room_category") != 0 and isinstance(data.get("room_category"), int) else RoomCategory.BOOKABLE_GROUP_ROOMS),
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
            day_str = f"{start_date.strftime('%A')}({start_date.year}-{start_date.month}-{start_date.day})"
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

    return " ".join(weeks_calendar)

def generate_week_calendar():
    today = datetime.datetime.now(pytz.timezone("Europe/Stockholm")).date()
    extended_days = [(today + datetime.timedelta(days=i)).strftime("%A, %B %d, %Y")
                    for i in range(15) if (today + datetime.timedelta(days=i)).weekday() < 5]
    return " ".join(extended_days)


def chat_completion(model: str, messages: List[Dict[str, str]]) -> Dict[str, str]:
    response = requests.post(
        f"{API_BASE_URL}{model}",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        json={"messages": messages},
        timeout=180,
    )
    return response.json()


def handle_message(history: List[Dict[str, str]], message: str, staff: bool = False):
    system_message: Dict[str, str] = {
        "role": "system",
        "content": f'''You assist with conversations and room scheduling

        Respond with JSON: {{"conversations_response": str, "requests": List[{{"date": "YYYY-MM-DD", "from_time": int 4 to 23 (hours), "duration": 1 to 4 (hours), breaks?: [{{"from_time": int 4 to 23 (hours), "duration": 1 to 4 (hours)}}], title?: str, {'room_category?: int, ' if staff else ''}room_filters?: List[int]}}]}} 

        Bookable dates/calender:
        {generate_week_calendar()}

        Info:
        * All times are 24-hour.
        * The user may provide times in the format XX-YY, this equals to from_time=XX and duration=YY-XX.
        * Booking hours are limited to whole hours between 04:00 (4) and 23:00 (23).
        * Current timestamp: {datetime.datetime.now(pytz.timezone("Europe/Stockholm")).strftime("%A, %B %d, %Y")}.
        * Earliest bookable time: {datetime.datetime.now(pytz.timezone("Europe/Stockholm")).hour+1:02}:00 (only applied for today)
        * request.date=today if a date/day isn't given by the user.
        * Each booking can last from 1 to 4 hours, excluding breaks.
        * The user will see the requests with buttons to confirm the request(s).
        * Users may specify breaks
        * Users may specify room_filters, one int per filter, combine by specifying multiple ints e.x. [1,2].
        Available room_filters: 0=G10_ROOM, 1=G5_ROOM, 2=GREEN_AREA, 3=RED_AREA. 0,1 and 2,3 are mutually exclusive.
        {"* The user is staff, they may specify a room_category." if staff else ""}
        {f"Available room_categories: {', '.join([f'{c.name}={c.value}' for c in RoomCategory])}, Note: NON_BOOKABLE_GROUP_ROOMS are bookable by staff." if staff else ""}
        '''.replace("    ", "")
    }
    context = [system_message] + history + [{"role": "user", "content": message}]# + [{"role": "assistant", "content": "<invalid json>"}] + [{"role": "assistant", "content": "please provide valid json"}]
    logging.debug("Context: %s", context)
    completion = chat_completion(
        #"@cf/meta-llama/llama-2-7b-chat-hf-lora", # good but added restriction
        # "@cf/google/gemma-7b-it-lora", # didnt complete
        # "@cf/mistral/mistral-7b-instruct-v0.2-lora", # didnt complete
        "@cf/meta/llama-3-8b-instruct", # generally good performance
        context,
    )
    logging.debug("Completion: %s", completion)
    out_message: str = completion["result"]["response"]  # type: ignore
    # Remove newlines/whitespace before and after json
    out_message = re.sub(r"^\s+", "", out_message)
    
    out_json = json.loads(out_message)
    if not isinstance(out_json, dict):
        raise json.decoder.JSONDecodeError("Expected JSON object", out_message, 0)

    parsed_requests = [RoomRequest.from_json(r) for r in out_json.get("requests", [])]

    return out_json.get("conversations_response", "<Empty response>"), out_json.get("requests", []), parsed_requests

def handle_message_retries(history: List[Dict[str, str]], message: str, staff: bool = False, retries: int = 5):
    prompt = message.strip()
    for i in range(max(retries, 1)):
        try:
            return handle_message(history, prompt, staff)
        except (json.JSONDecodeError, ValueError) as e:
            if retries - 1 == i:
                raise e
            
            # First retry nothing changes, due to to the randomness of LLM it could be result in the correct result on a later retry
            logging.warning("LLM Encountered an error, %s: %s, retrying %s more times", type(e), e, retries - i - 1)
            if i == 0:
                continue

            history += [{"role": "user", "content": prompt}]
            history += [{"role": "assistant", "content": f"<invalid output, error: f{type(e)}: {e}>"}]
            prompt = "<provide valid json without any other characters before or after it>"

    # Would use Never type but not available in the python version I'm using 
    raise RuntimeError("Impossible outcome")
