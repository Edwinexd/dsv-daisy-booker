from daisy import Room, RoomCategory, RoomTime, add_booking_user, create_booking


if __name__ == "__main__":
    # Example usage
    response_text = add_booking_user(
        year="2024",
        month="04",
        day="14",
        from_time=RoomTime.NINE,
        to_time=RoomTime.TEN,
        room_category=RoomCategory.BOOKABLE_GROUP_ROOMS,
        room_id=Room.G10_1.value,
        search_term="Thea Ekmark",
        lagg_till_person_id=175770,
    )
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
