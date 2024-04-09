import os
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

def add_booking_user(year, month, day, from_time: RoomTime, to_time: RoomTime, room_category: RoomCategory, room_id: int, search_term: str, lagg_till_person_id: int):
    if from_time >= to_time:
        raise ValueError("from_time must be before to_time")
    
    url = "https://daisy.dsv.su.se/common/schema/bokning.jspa"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"JSESSIONID={JSESSIONID};"
    }
    data = {
        "year": year,
        "month": month,
        "day": day,
        "from": from_time.to_string(),
        "to": to_time.to_string(),
        "lokalkategoriID": room_category.to_string(),
        "lokalID": room_id,
        "namn": "",
        "descr": "",
        "searchTerm": search_term,
        "laggTillPersonID": lagg_till_person_id,
    }
    
    response = requests.post(url, headers=STANDARD_HEADERS | headers, data=data)
    return response

def create_booking(year, month, day, from_time: RoomTime, to_time: RoomTime, room_category: RoomCategory, room_id: int, namn: str, description: Optional[str] = None):
    url = "https://daisy.dsv.su.se/common/schema/bokning.jspa"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"JSESSIONID={JSESSIONID};"
    }
    data = {
        "year": year,
        "month": month,
        "day": day,
        "from": from_time.to_string(),
        "to": to_time.to_string(),
        "lokalkategoriID": room_category.to_string(),
        "lokalID": room_id,
        "namn": namn,
        "descr": description if description else "",
        "searchTerm": "",
        "laggTillPersonID": "",
        "bokning": ""
    }
    
    response = requests.post(url, headers=STANDARD_HEADERS | headers, data=data)
    return response

