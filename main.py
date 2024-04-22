import os
from daisy import Room, RoomCategory, RoomTime, add_booking_user, create_booking, get_schedule_for_category
from parse import parse_daisy_schedule
from scheduler import BookableRoom, schedule
import datetime

import dotenv
dotenv.load_dotenv()


if __name__ == "__main__":
    ROOM_TITLE = "PVT"
    DATE = datetime.date(2024, 5, 3)
    
    response_text = add_booking_user(
        date=DATE,
        search_term=os.getenv("SECOND_USER_SEARCH_TERM"), # type: ignore
        lagg_till_person_id=int(os.getenv("SECOND_USER_ID")), # type: ignore
    )

    schedule_html = get_schedule_for_category(DATE, RoomCategory.BOOKABLE_GROUP_ROOMS)
    parsed_schedule = parse_daisy_schedule(schedule_html)
    activities = parsed_schedule.activities
    rooms = [BookableRoom(name, activities[name]) for name in activities.keys()]
    # Order the rooms so that G10_2 is first, then G10_7, G10_6 then all other G10 rooms, then all G5 rooms except G5_12
    rooms = sorted(rooms, key=lambda room: (
        Room.G10_2.value == Room.from_name(room.name).value,
        Room.G10_7.value == Room.from_name(room.name).value,
        Room.G10_6.value == Room.from_name(room.name).value,
        Room.from_name(room.name).value == Room.G10_3.value,
        Room.from_name(room.name).value == Room.G10_4.value,
        Room.from_name(room.name).value == Room.G10_5.value,
        Room.from_name(room.name).value == Room.G10_1.value,
        Room.from_name(room.name).value == Room.G5_1.value,
        Room.from_name(room.name).value == Room.G5_2.value,
        Room.from_name(room.name).value == Room.G5_3.value,
        Room.from_name(room.name).value == Room.G5_4.value,
        Room.from_name(room.name).value == Room.G5_5.value,
        Room.from_name(room.name).value == Room.G5_6.value,
        Room.from_name(room.name).value == Room.G5_7.value,
        Room.from_name(room.name).value == Room.G5_8.value,
        Room.from_name(room.name).value == Room.G5_9.value,
        Room.from_name(room.name).value == Room.G5_10.value,
        Room.from_name(room.name).value == Room.G5_11.value,
        Room.from_name(room.name).value == Room.G5_13.value,
        Room.from_name(room.name).value == Room.G5_15.value,
        Room.from_name(room.name).value == Room.G5_16.value,
        Room.from_name(room.name).value == Room.G5_17.value,
    ), reverse=True)
    for time in [RoomTime.TEN, RoomTime.THIRTEEN]:
        suggestion = schedule(rooms, time, 2, shift=True)
        # TODO Confirm suggestion with user
        for entry in suggestion:
            # Book each room
            response = create_booking(
                date=DATE,
                from_time=entry.from_time,
                to_time=entry.to_time,
                room_category=RoomCategory.BOOKABLE_GROUP_ROOMS,
                room_id=Room.from_name(entry.room_name).value,
                name=ROOM_TITLE,
            )
        print(suggestion)
        
    raise SystemExit()
