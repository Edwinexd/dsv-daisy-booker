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

import attr

from daisy import RoomTime
from parse import RoomActivity

@attr.s(auto_attribs=True, frozen=True, slots=True)
class BookingSlot:
    room_name: str
    from_time: RoomTime
    to_time: RoomTime

@attr.s(auto_attribs=True, frozen=True, slots=True)
class BookableRoom:
    name: str
    booked_slots: List[RoomActivity]

def schedule(rooms: List[BookableRoom], start_time: RoomTime, hours: int, shift: bool = False) -> List[BookingSlot]:
    """
    Schedule a meeting in a room

    Args:
        rooms: All rooms that are allowed to be used for the meeting, sorted in order of preference
        start_time: Start time of the meeting
        hours: Duration of the meeting in hours
        shift: If getting the right amount of hours is more important than the start time

    Returns:
        List[BookingSlot]: List of suggested bookings to cover the meeting
    """

    room_max_name = ""
    room_max_hours = -1

    for room in rooms:
        room_name = room.name
        booked_slots = room.booked_slots
        booked_hours = 0

        start_hours = start_time.value
        for i in range(start_hours, hours + start_hours):
            if i >= 23:
                break
            if RoomTime(i) not in [slot.time_slot_start for slot in booked_slots]:
                booked_hours += 1
            else:
                break

        if booked_hours > room_max_hours:
            room_max_hours = booked_hours
            room_max_name = room_name

    result = []

    if room_max_hours > 0:
        result.append(BookingSlot(room_max_name, start_time, RoomTime(start_hours + room_max_hours)))
    
    if room_max_hours + start_hours == 23:
        return result

    if room_max_hours < hours:
        if room_max_hours == 0:
            # If we couldn't book any hours in any room we may shift the booking to the next hour
            if shift:
                start_hours += 1
                start_time = RoomTime(start_hours)
                return schedule(rooms, start_time, hours, shift=True)
            room_max_hours = 1
        # Attempt to book the remaining hours in another room
        remaining_hours = hours - room_max_hours
        remaining_start_time = RoomTime(start_hours + room_max_hours)

        remaining_result = schedule(rooms, remaining_start_time, remaining_hours, shift=shift)
        result.extend(remaining_result)

    return result
