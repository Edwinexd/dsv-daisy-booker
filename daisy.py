import os
import datetime
from enum import Enum
from typing import Optional

import dotenv
import requests

dotenv.load_dotenv()

JSESSIONID = os.getenv("JSESSIONID")

STANDARD_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,sv;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "daisy.dsv.su.se",
    "Origin": "https://daisy.dsv.su.se",
    "Referer": "https://daisy.dsv.su.se/common/schema/bokning.jspa",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "sec-ch-ua": '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "X-Powered-By": "dsv-daisy-booker (https://github.com/Edwinexd/dsv-daisy-booker); Contact (edwin.sundberg@dsv.su.se)",
}

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

def add_booking_user(date: datetime.date, search_term: str, lagg_till_person_id: int):
    url = "https://daisy.dsv.su.se/common/schema/bokning.jspa"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"JSESSIONID={JSESSIONID};"
    }
    data = {
        "year": date.year,
        "month": f"{date.month:02d}",
        "day": f"{date.day:02d}",
        "from": RoomTime.NINE.to_string(),
        "to": RoomTime.TEN.to_string(),
        "lokalkategoriID": RoomCategory.BOOKABLE_GROUP_ROOMS.to_string(),
        "lokalID": Room.G10_1.value,
        "namn": "",
        "descr": "",
        "searchTerm": search_term,
        "laggTillPersonID": lagg_till_person_id,
    }
    
    response = requests.post(url, headers=STANDARD_HEADERS | headers, data=data)
    return response

def create_booking(date: datetime.date, from_time: RoomTime, to_time: RoomTime, room_category: RoomCategory, room_id: int, name: str, description: Optional[str] = None):
    url = "https://daisy.dsv.su.se/common/schema/bokning.jspa"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"JSESSIONID={JSESSIONID};"
    }
    data = {
        "year": date.year,
        "month": f"{date.month:02d}",
        "day": f"{date.day:02d}",
        "from": from_time.to_string(),
        "to": to_time.to_string(),
        "lokalkategoriID": room_category.to_string(),
        "lokalID": room_id,
        "namn": name,
        "descr": description if description else "",
        "searchTerm": "",
        "laggTillPersonID": "",
        "bokning": ""
    }
    
    response = requests.post(url, headers=STANDARD_HEADERS | headers, data=data)
    return response

def get_schedule_for_category(date: datetime.date, room_category: RoomCategory):
    # https://daisy.dsv.su.se/servlet/schema.LokalSchema
    # url-en
    # lokalkategori: 68
    # year: 2024
    # month: 04
    # day: 17
    # datumSubmit: Visa
    url = "https://daisy.dsv.su.se/servlet/schema.LokalSchema"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"JSESSIONID={JSESSIONID};"
    }
    data = {
        "lokalkategori": room_category.to_string(),
        "year": date.year,
        "month": f"{date.month:02d}",
        "day": f"{date.day:02d}",
        "datumSubmit": "Visa"
    }
    response = requests.post(url, headers=STANDARD_HEADERS | headers, data=data)
    return response.text

def is_token_valid() -> bool:
    url = "https://daisy.dsv.su.se/servlet/schema.LokalSchema"
    headers = {
        "Cookie": f"JSESSIONID={JSESSIONID};",
        "Referer": "https://daisy.dsv.su.se/student/aktuellt.jspa"
    }

    response = requests.get(url, headers=STANDARD_HEADERS | headers)
    return "Log in" not in response.text
