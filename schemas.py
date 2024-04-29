import datetime
from enum import Enum
from typing import Callable, Dict, List

import attr


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
    VISITORS_MEETING_ROOMS = 81
    COMPUTER_LABS = 66
    DISTANCE_AND_RECORDING_STUDIOS = 95
    BOOKABLE_GROUP_ROOMS = 68
    NON_BOOKABLE_GROUP_ROOMS = 77
    MEDIA_PRODUCTION = 76
    PROJECT_MEETING_ROOMS = 82
    MEETING_ROOMS = 71
    SEMINAR_ROOMS = 67
    STUDENT_LAB = 65
    TEACHING_ROOMS = 64

    def to_string(self):
        return str(self.value)

class Room(Enum):
    # Bookable group rooms
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
    # Visitors meeting rooms
    F1 = 840
    F2 = 839
    F3 = 838
    # Computer labs
    D1 = 625
    D2 = 626
    D3 = 627
    D4 = 628
    # Distance and recording studios
    IDEAL_STUDIO = 790
    SMALL_STUDIO = 1275
    # Unbookable group rooms
    G10_8 = 640
    G5_14 = 813
    G5_18 = 809
    G5_19 = 808
    G5_20 = 807
    G5_21 = 806
    # Media production
    P1 = 652
    P2 = 653
    P3 = 654
    STUDENTLABB_MEDIA = 651
    STUDIO = 655
    # Project meeting rooms
    PROJECT_ZONE_2 = 1257
    PROJECT_ZONE_5 = 1258
    # Meeting rooms
    M10 = 817
    M20 = 820
    M6_1 = 823
    M6_2 = 822
    M6_3 = 821
    M6_4 = 824
    M6_5 = 825
    M6_6 = 819
    M8 = 818
    # Seminar rooms
    S1 = 629
    S2 = 630
    S3 = 631
    # Student lab
    STUDENTLABB_ID_RIGHT = 648
    STUDENTLABB_ID_LEFT = 1378
    STUDENTLABB_ID_FIX = 1382
    STUDENTLABB_GAME = 1394
    STUDENTLABB_GAME_2022 = 649
    STUDENTLABB_GAME_EXTRA_2022 = 869
    STUDENTLABB_SECURITY = 650
    # Teaching rooms
    AUDITORIUM_NOD = 620
    DL_40 = 632
    L30 = 622
    L50 = 623
    L70 = 624
    SMALL_AUDITORIUM = 621

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
            "G5:9": cls.G5_9,
            # Foaje
            "Foaje F1": cls.F1,
            "Foaje F2": cls.F2,
            "Foaje F3": cls.F3,
            # Datorsalar
            "D1": cls.D1,
            "D2": cls.D2,
            "D3": cls.D3,
            "D4": cls.D4,
            # Distans och inspelningsstudios
            "IDEAL-studion": cls.IDEAL_STUDIO,
            "Lilla studion": cls.SMALL_STUDIO,
            # Unbookable group rooms
            "G10:8": cls.G10_8,
            "G5:14": cls.G5_14,
            "G5:18": cls.G5_18,
            "G5:19": cls.G5_19,
            "G5:20": cls.G5_20,	
            "G5:21": cls.G5_21,
            # Mediaproduktion
            "Produktion 1": cls.P1,
            "Produktion 2": cls.P2,
            "Produktion 3": cls.P3,
            "Studentlabb Media": cls.STUDENTLABB_MEDIA,
            "Studio": cls.STUDIO,
            # Projektmötesrum
            "Projektmöte Zon 2": cls.PROJECT_ZONE_2,
            "Projektmöte Zon 5": cls.PROJECT_ZONE_5,
            # Mötesrum
            "M10": cls.M10,
            "M20": cls.M20,
            "M6:1": cls.M6_1,
            "M6:2": cls.M6_2,
            "M6:3": cls.M6_3,
            "M6:4": cls.M6_4,
            "M6:5": cls.M6_5,
            "M6:6": cls.M6_6,
            "M8": cls.M8,
            # Seminarierum
            "S1": cls.S1,
            "S2": cls.S2,
            "S3": cls.S3,
            # Studentlabb
            "Studentlabb ID Höger": cls.STUDENTLABB_ID_RIGHT,
            "Studentlabb ID Vänster": cls.STUDENTLABB_ID_LEFT,
            "Studentlabb ID:fix": cls.STUDENTLABB_ID_FIX,
            "Studentlabb Spel": cls.STUDENTLABB_GAME,
            "Studentlabb Spel (-2022)": cls.STUDENTLABB_GAME_2022,
            "Studentlabb Spel extra (-2022)": cls.STUDENTLABB_GAME_EXTRA_2022,
            "Studentlabb Säkerhet": cls.STUDENTLABB_SECURITY,
            # Undervisningsrum
            "Aula NOD": cls.AUDITORIUM_NOD,
            "DL40": cls.DL_40,
            "L30": cls.L30,
            "L50": cls.L50,
            "L70": cls.L70,
            "Lilla Hörsalen": cls.SMALL_AUDITORIUM,
        }[name]

class RoomRestriction(Enum):
    G10_ROOM = 0
    G5_ROOM = 1
    GREEN_AREA = 2
    RED_AREA = 3

    def to_string(self):
        return str(self.value)
    
    def to_filter(self) -> Callable[[Room], bool]:
        if self == RoomRestriction.G10_ROOM:
            return lambda room: room in [Room.G10_1, Room.G10_2, Room.G10_3, Room.G10_4, Room.G10_5, Room.G10_6, Room.G10_7]
        if self == RoomRestriction.G5_ROOM:
            return lambda room: room in [Room.G5_1, Room.G5_10, Room.G5_11, Room.G5_12, Room.G5_13, Room.G5_15, Room.G5_16, Room.G5_17, Room.G5_2, Room.G5_3, Room.G5_4, Room.G5_5, Room.G5_6, Room.G5_7, Room.G5_8, Room.G5_9]
        if self == RoomRestriction.GREEN_AREA:
            return lambda room: room in [Room.G10_1, Room.G10_2, Room.G10_3, Room.G10_4, Room.G10_5, Room.G5_1, Room.G5_10, Room.G5_11, Room.G5_12, Room.G5_2, Room.G5_3, Room.G5_4, Room.G5_5, Room.G5_6, Room.G5_7, Room.G5_8, Room.G5_9]
        if self == RoomRestriction.RED_AREA:
            return lambda room: room in [Room.G10_6, Room.G10_7, Room.G5_13, Room.G5_15, Room.G5_16, Room.G5_17]
        
        raise KeyError(f"Unknown restriction {self}")

@attr.s(auto_attribs=True, frozen=True, slots=True)
class BookingSlot:
    room: Room
    from_time: RoomTime
    to_time: RoomTime

@attr.s(auto_attribs=True, frozen=True, slots=True)
class RoomActivity:
    time_slot_start: RoomTime
    time_slot_end: RoomTime
    event: str

@attr.s(auto_attribs=True, frozen=True, slots=True)
class BookableRoom:
    room: Room
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
