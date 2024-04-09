# {
#     room_name: [
#         {
#             "time_slot_start": str, # 09:00
#             "time_slot_end": str, # 10:00
#             "event": str
#         }
#     ]
# }

from datetime import timedelta
import datetime
from typing import Any, Dict, List


def schedule(rooms: Dict[str, Any], start_time: str, hours: int, shift: bool = False) -> List[Dict[str, str]]:
    """
    Schedule a meeting in a room

    Args:
        rooms (Dict[str, Any]): {
            room_name: [
                {
                    "time_slot_start": str, # 09:00
                    "time_slot_end": str, # 10:00
                    "event": str
                }
            ]
        } All rooms that are allowed to be used
        start_time: Start time of the meeting in format "HH:MM"
        hours: Duration of the meeting in hours
        shift: If getting the right amount of hours is more important than the start time

    Returns:
        List[Dict[str, str]]: [
            {
                "room_name": str,
                "time_slot_start": str, # 09:00
                "time_slot_end": str, # 10:00
            }
        ]
    """
    if start_time == "24:00":
        return []

    def format_hour(hour: int) -> str:
        return f"{hour:02}:00"

    room_max_name = ""
    room_max_hours = -1

    for room_name, booked_slots in rooms.items():
        booked_hours = 0

        start_hours = int(start_time.split(":")[0])
        for i in range(start_hours, hours + start_hours):
            if format_hour(i) not in [slot["time_slot_start"] for slot in booked_slots]:
                booked_hours += 1
            else:
                break

        if booked_hours > room_max_hours:
            room_max_hours = booked_hours
            room_max_name = room_name

    result = []

    if room_max_hours > 0:
        result.append({
            "room_name": room_max_name,
            "time_slot_start": start_time,
            "time_slot_end": format_hour(start_hours + room_max_hours)
        })
    
    if room_max_hours < hours:
        if room_max_hours == 0:
            # If we couldn't book any hours in any room we may shift the booking to the next hour
            if shift:
                start_hours += 1
                start_time = format_hour(start_hours)
                return schedule(rooms, start_time, hours, shift=True)
            room_max_hours = 1
        # Attempt to book the remaining hours in another room
        remaining_hours = hours - room_max_hours
        remaining_start_time = format_hour(start_hours + room_max_hours)

        remaining_result = schedule(rooms, remaining_start_time, remaining_hours, shift=shift)
        result.extend(remaining_result)

    return result
