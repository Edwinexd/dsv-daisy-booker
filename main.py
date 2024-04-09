import os
from daisy import Room, RoomCategory, RoomTime, add_booking_user, create_booking, get_schedule_for_category
from parse import parse_daisy_schedule
from scheduler import schedule


if __name__ == "__main__":
    response_text = add_booking_user(
        year="2024",
        month="04",
        day="14",
        from_time=RoomTime.NINE,
        to_time=RoomTime.TEN,
        room_category=RoomCategory.BOOKABLE_GROUP_ROOMS,
        room_id=Room.G10_1.value,
        search_term=os.getenv("SECOND_USER_SEARCH_TERM"), # type: ignore
        lagg_till_person_id=int(os.getenv("SECOND_USER_ID")), # type: ignore
    )
    schedule_html = get_schedule_for_category("2024", "04", "16", RoomCategory.BOOKABLE_GROUP_ROOMS)
    parsed_schedule = parse_daisy_schedule(schedule_html)
    activities = parsed_schedule.activities
    suggestion = schedule({room: slots for room, slots in activities.items() if room.startswith("G10")}, RoomTime.THIRTEEN, 3, shift=True)
    # TODO Confirm suggestion with user
    for entry in suggestion:
        # Book each room
        response = create_booking(
            year="2024",
            month="04",
            day="16",
            from_time=entry.from_time,
            to_time=entry.to_time,
            room_category=RoomCategory.BOOKABLE_GROUP_ROOMS,
            room_id=Room.from_name(entry.room_name).value,
            namn="PVT",
        )
    print(suggestion)

    raise SystemExit()
    # Example usage

    print(response_text)

    response = create_booking(
        year="2024",
        month="04",
        day="14",
        from_time=RoomTime.NINE,
        to_time=RoomTime.TEN,
        room_category=RoomCategory.BOOKABLE_GROUP_ROOMS,
        room_id=Room.G10_1.value,
        namn="PVT",
    )
    print(response.status_code)
    print(response.text)
