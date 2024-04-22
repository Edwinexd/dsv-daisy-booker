from typing import List, Tuple
import attr
from daisy import Room, RoomCategory, RoomTime, add_booking_user, create_booking, get_schedule_for_category, is_token_valid
from parse import parse_daisy_schedule
from scheduler import BookableRoom, BookingSlot, schedule
import datetime
import os

import dotenv

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

def schedule_rooms(date: datetime.date, from_time: RoomTime, duration: int, breaks: List[Break]) -> List[BookingSlot]:
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
            remaining_hours_after_break = prev_time[1] - (break_.start_time.value - prev_time[0].value)
            times.append((prev_time[0], break_.start_time.value - prev_time[0].value))
            times.append((RoomTime(next_start_time), remaining_hours_after_break))

    all_times = []
    for start_time, slot_duration in times:
        suggestion = schedule(rooms, start_time, slot_duration, shift=True)
        for entry in suggestion:
            all_times.append(entry)

    return all_times

def book_rooms(times: List[BookingSlot], date: datetime.date, title: str):
    for entry in times:
        # Book each room
        response = create_booking(
            date=date,
            from_time=entry.from_time,
            to_time=entry.to_time,
            room_category=RoomCategory.BOOKABLE_GROUP_ROOMS,
            room_id=Room.from_name(entry.room_name).value,
            name=title,
        )

if __name__ == "__main__":
    dotenv.load_dotenv()

    assert is_token_valid()

    DATE = datetime.date(2024, 4, 27)
    ROOM_TITLE = "PVT"

    add_booking_user(
        date=DATE,
        search_term=os.getenv("SECOND_USER_SEARCH_TERM"), # type: ignore
        lagg_till_person_id=int(os.getenv("SECOND_USER_ID")), # type: ignore
    )

    s = schedule_rooms(DATE, RoomTime.TEN, 4, [Break(RoomTime.TWELVE, 1)])
    print(s)
    book_rooms(s, DATE, ROOM_TITLE)
