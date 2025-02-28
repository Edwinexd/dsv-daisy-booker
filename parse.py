"""
A discord bot capable of booking student group rooms and staff rooms via Daisy (administration tool for Department of Computer and Systems Sciences at Stockholm University)
Copyright (C) 2024 Edwin Sundberg

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import datetime
import re
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup

from schemas import RoomCategory, RoomTime, Schedule, RoomActivity

def parse_daisy_schedule(html_content: str) -> Schedule:
    """
    Parse Daisy schedule from html content to a structured json format using BeautifulSoup

    Args:
        html_content: HTML content of the schedule
    
    Returns:
        Schedule object containing the parsed schedule
    """
    # Initialize BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the table containing the schedule
    # This assumes there's a unique table for the schedule, may need adjustment for the actual structure
    schedule_table = soup.find("table", {"class": "bgTabell"})

    rows = schedule_table.find_all("tr") # type: ignore

    room_names = [td.text for td in rows[1].find_all("td")[1:]]

    room_events: List[List[Tuple[str, str]]] = [[] for _ in room_names]
    room_offsets = [0] * len(room_names)

    for row in rows[2:]:
        cells = row.find_all("td")
        time_slot = cells[0].text.strip()
        slicer = 0
        for i in range(len(room_names)):
            if room_offsets[i] > 0:
                room_events[i].append((time_slot, room_events[i][-1][1]))
                room_offsets[i] -= 1
                continue
            cell = cells[slicer + 1]
            if cell.find("a") and (cell.get("rowspan") or cell.text.strip()):
                event = list(cell.find("a").children)[0].strip()
                duration = cell.find("span", {"class": "mini"}).text.split(": ")[1]
                row_span = int(cell.get("rowspan") or 1)
                start_hour = int(duration.split("-")[0])
                end_hour = start_hour + row_span
                event_time_slots = [
                    f"{hour:02d}-{hour + 1:02d}" for hour in range(start_hour, end_hour)
                ]
                room_events[i].append((time_slot, event))
                room_offsets[i] = len(event_time_slots) - 1
            slicer += 1


    # Format to pretty, usable json
    # { room_name: [ { time_slot_start: str, time_slot_end: str, event: str } ] } # one entry for each hour if event spans multiple hours
    room_events_dict = {}
    for i, room in enumerate(room_names):
        room_events_dict[room] = []
        for time_slot, event in room_events[i]:
            room_events_dict[room].append(
                {
                    "time_slot_start": int(time_slot.split("-")[0]),
                    "time_slot_end": int(time_slot.split("-")[1]),
                    "event": event,
                }
            )


    # Assemble datatime & other metadata
    room_category_title = rows[0].find_all("td")[1].find("b").text
    room_category_id = (
        rows[0]
        .find_all("td")[1]
        .find("a")
        .get_attribute_list("href")[0]
        .split("&")[1]
        .split("=")[1]
    )
    date_column = list(rows[0].find_all("td")[1].children)[2]

    date_match = re.findall(r"(\d{4})-(\d{2})-(\d{2})", date_column)[0]
    date = datetime.datetime(int(date_match[0]), int(date_match[1]), int(date_match[2]))

    return Schedule(
        {k:[RoomActivity(RoomTime(activity["time_slot_start"]), RoomTime(activity["time_slot_end"]), activity["event"]) for activity in v] for k, v in room_events_dict.items()},
        room_category_title,
        int(room_category_id),
        RoomCategory(int(room_category_id)),
        date
    )

def parse_booking_completion(html_content: str) -> Optional[str]:
    soup = BeautifulSoup(html_content, "html.parser")
    # <ul class="errorMessage">
    # <li><span>Du måste ange en titel.</span></li>	</ul>
    error_message = soup.find("ul", {"class": "errorMessage"})
    if error_message:
        return error_message.find("span").text # type: ignore
    
    return None

