from typing import List, Optional, Tuple

from schemas import BookableRoom, Room, RoomRestriction, RoomTime, Schedule, Break, BookingSlot


# TODO: User-variable:
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
    # Visitors meeting rooms
    Room.F1,
    Room.F3,
    # No preference for computer labs
    # No preference for distance and recording studios
    # Unbookable group rooms:
    Room.G10_8,
    # ^ Rest of the rooms, no preference
    # No preference for media production rooms
    # Project meeting rooms
    Room.PROJECT_ZONE_5,
    Room.PROJECT_ZONE_2,
    # (Staff) meeting rooms
    Room.M6_5,
    Room.M6_6,
    # ^ Rest of the rooms, no preference
    # Seminar rooms
    Room.S2,
    Room.S1,
    Room.S3,
    # No preference for student labs
    # Teaching rooms
    Room.AUDITORIUM_NOD,
    Room.SMALL_AUDITORIUM,
    Room.L70,
    Room.L50,
    Room.L30,
]

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

    start_hours = start_time.value

    room_max: Optional[BookableRoom] = None
    room_max_hours = -1

    for room in rooms:
        booked_slots = room.booked_slots
        booked_hours = 0

        for i in range(start_hours, hours + start_hours):
            if i >= 23:
                break
            if RoomTime(i) not in [slot.time_slot_start for slot in booked_slots]:
                booked_hours += 1
            else:
                break

        if booked_hours > room_max_hours:
            room_max_hours = booked_hours
            room_max = room

    result = []

    if room_max_hours > 0 and room_max is not None:
        result.append(BookingSlot(room_max.room, start_time, RoomTime(start_hours + room_max_hours)))
    
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

def schedule_rooms(category_schedule: Schedule, from_time: RoomTime, duration: int, breaks: List[Break], room_restrictions: List[RoomRestriction]) -> List[BookingSlot]:
    """Higher level function to schedule rooms with support for breaks"""
    # TODO: BookableRoom has to use the enum!
    rooms = [BookableRoom(Room.from_name(name), value) for name, value in category_schedule.activities.items()]

    for restriction in room_restrictions:
        func = restriction.to_filter()
        rooms = [room for room in rooms if func(room.room)]

    # Order rooms after preference, note: not all rooms are included in ROOM_PREFERENCE_ORDER
    rooms = sorted(rooms, key=lambda room: ROOM_PREFERENCE_ORDER.index(room.room) if room.room in ROOM_PREFERENCE_ORDER else len(ROOM_PREFERENCE_ORDER))

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
