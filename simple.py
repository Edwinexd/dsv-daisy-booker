from typing import List, Tuple
import attr
from daisy import Room, RoomCategory, RoomTime, add_booking_user, create_booking, get_schedule_for_category
from parse import parse_daisy_schedule
from scheduler import BookableRoom, schedule
import datetime

# TODO: User-variables:
ROOM_PREFERENCE_ORDER = [
    Room.G10_2,
    Room.G10_7,
    Room.G10_6,
    Room.G10_3,
    Room.G10_4,
    Room.G10_5,
    Room.G10_1,
    Room.G5_1,
    Room.G5_2,
    Room.G5_3,
    Room.G5_4,
    Room.G5_5,
    Room.G5_6,
    Room.G5_7,
    Room.G5_8,
    Room.G5_9,
    Room.G5_10,
    Room.G5_11,
    Room.G5_13,
    Room.G5_15,
    Room.G5_16,
    Room.G5_17,
]



@attr.s(auto_attribs=True, frozen=True, slots=True)
class Break:
    start_time: RoomTime
    duration: int

def schedule_and_book_room(date: datetime.date, title: str, from_time: RoomTime, duration: int, breaks: List[Break]):
    """Assumes booking companion has been set up"""
    schedule_html = get_schedule_for_category(date, RoomCategory.BOOKABLE_GROUP_ROOMS)
    parsed_schedule = parse_daisy_schedule(schedule_html)
    activities = parsed_schedule.activities # pylint: disable=no-member
    rooms = [BookableRoom(name, activities[name]) for name in activities.keys()]

    # Order rooms after preference, note: not all rooms are included in ROOM_PREFERENCE_ORDER
    rooms = sorted(rooms, key=lambda room: ROOM_PREFERENCE_ORDER.index(Room.from_name(room.name)) if Room.from_name(room.name) in ROOM_PREFERENCE_ORDER else len(ROOM_PREFERENCE_ORDER))

    times: List[Tuple[RoomTime, int]] = [(from_time, duration)] # list of start times and durations
    if breaks:
        for break_ in breaks:
            prev_time = times.pop()
            next_start_time = break_.start_time.value + break_.duration
            remaining_hours_after_break = prev_time[0].value + prev_time[1] - next_start_time
            times.append((prev_time[0], break_.start_time.value - prev_time[0].value))

