import attr

from enum import Enum

import datetime

from typing import List, Dict

class RoomTime(Enum):
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    ELEVEN = 11
    TWELVE = 12
    THIRTEEN = 13
    FOURTEEN = 14
    FIFTEEN = 15
    SIXTEEN = 16
    SEVENTEEN = 17
    EIGHTEEN = 18
    NINETEEN = 19
    TWENTY = 20
    TWENTY_ONE = 21
    TWENTY_TWO = 22
    TWENTY_THREE = 23

    def to_string(self):
        if self.value < 10:
            return f"0{self.value}:00"
        return f"{self.value}:00"

    def __lt__(self, other):
        return self.value < other.value
    
    def __le__(self, other):
        return self.value <= other.value
    
    def __eq__(self, other):
        return self.value == other.value
    
    def __ne__(self, other):
        return self.value != other.value
    
    def __gt__(self, other):
        return self.value > other.value
    
    def __ge__(self, other):
        return self.value >= other.value

class RoomCategory(Enum):
    BOOKABLE_GROUP_ROOMS = 68

    def to_string(self):
        return str(self.value)

class Room(Enum):
    G10_1 = 633
    G10_2 = 634
    G10_3 = 635
    G10_4 = 636
    G10_5 = 637
    G10_6 = 638
    G10_7 = 639
    G5_1 = 815
    G5_10 = 804
    G5_11 = 805
    G5_12 = 795
    G5_13 = 814
    G5_15 = 812
    G5_16 = 811
    G5_17 = 810
    G5_2 = 796
    G5_3 = 797
    G5_4 = 798
    G5_5 = 799
    G5_6 = 800
    G5_7 = 801
    G5_8 = 802
    G5_9 = 803

    @classmethod
    def from_name(cls, name: str):
        return {
            "G10:1": cls.G10_1,
            "G10:2": cls.G10_2,
            "G10:3": cls.G10_3,
            "G10:4": cls.G10_4,
            "G10:5": cls.G10_5,
            "G10:6": cls.G10_6,
            "G10:7": cls.G10_7,
            "G5:1": cls.G5_1,
            "G5:10": cls.G5_10,
            "G5:11": cls.G5_11,
            "G5:12": cls.G5_12,
            "G5:13": cls.G5_13,
            "G5:15": cls.G5_15,
            "G5:16": cls.G5_16,
            "G5:17": cls.G5_17,
            "G5:2": cls.G5_2,
            "G5:3": cls.G5_3,
            "G5:4": cls.G5_4,
            "G5:5": cls.G5_5,
            "G5:6": cls.G5_6,
            "G5:7": cls.G5_7,
            "G5:8": cls.G5_8,
            "G5:9": cls.G5_9
        }[name]

@attr.s(auto_attribs=True, frozen=True, slots=True)
class BookingSlot:
    room_name: str
    from_time: RoomTime
    to_time: RoomTime

@attr.s(auto_attribs=True, frozen=True, slots=True)
class RoomActivity:
    time_slot_start: RoomTime
    time_slot_end: RoomTime
    event: str

@attr.s(auto_attribs=True, frozen=True, slots=True)
class BookableRoom:
    name: str
    booked_slots: List[RoomActivity]

@attr.s(auto_attribs=True, frozen=True, slots=True)
class Schedule:
    activities: Dict[str, List[RoomActivity]]
    room_category_title: str
    room_category_id: int
    room_category: RoomCategory
    datetime: datetime.datetime

@attr.s(auto_attribs=True, frozen=True, slots=True)
class Break:
    start_time: RoomTime
    duration: int
