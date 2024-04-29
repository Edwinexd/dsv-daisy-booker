import os
import datetime
from enum import Enum
from typing import List, Optional

import requests

from login import daisy_login
from parse import parse_daisy_schedule
from schemas import BookingSlot, Schedule, RoomCategory, Room, RoomTime

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

class Daisy:
    def __init__(self, su_username: str, su_password: str, search_term: str, lagg_till_person_id: int, initial_jsessionid: Optional[str] = None, last_validated: Optional[datetime.datetime] = None, booking_user_added: bool = False, staff: bool = False, staff_jsessionid: Optional[str] = None, staff_last_validated: Optional[datetime.datetime] = None):
        self.__su_username: str = su_username
        self.__su_password: str = su_password
        self.search_term: str = search_term
        self.lagg_till_person_id: int = lagg_till_person_id
        self.jsessionid = initial_jsessionid
        self.last_validated = last_validated
        self.booking_user_added = booking_user_added
        self.staff = staff
        self.staff_jsessionid = staff_jsessionid
        self.staff_last_validated = staff_last_validated

    def _ensure_valid_jsessionid(self):
        if self.jsessionid is not None and self.last_validated is not None and datetime.datetime.now().date == self.last_validated.date and self.last_validated.hour != datetime.datetime.now().hour:
            # Token does not need to be rechecked at the moment
            return
        
        if self.jsessionid is not None and self._is_token_valid():
            self.last_validated = datetime.datetime.now()
            return
        
        self.jsessionid = daisy_login(self.__su_username, self.__su_password)
        self.booking_user_added = False
        self.last_validated = datetime.datetime.now()

    def _ensure_valid_staff_jsessionid(self):
        if self.staff_jsessionid is not None and self.staff_last_validated is not None and datetime.datetime.now().date == self.staff_last_validated.date and self.staff_last_validated.hour != datetime.datetime.now().hour:
            # Token does not need to be rechecked at the moment
            return
        
        if self.staff_jsessionid is not None and self._is_staff_token_valid():
            self.staff_last_validated = datetime.datetime.now()
            return

        if not self.staff:
            raise ValueError("Staff token requested but staff is not enabled")
        
        self.staff_jsessionid = daisy_login(self.__su_username, self.__su_password, staff=True)
        self.staff_last_validated = datetime.datetime.now()

    # Before request function wrapper
    def _ensure_valid_jsessionid_wrapper(self, func):
        def wrapper(self, *args, **kwargs):
            self._ensure_valid_jsessionid()
            return func(self, *args, **kwargs)
        return wrapper

    def _is_token_valid(self) -> bool:
        url = "https://daisy.dsv.su.se/servlet/schema.LokalSchema"
        headers = {
            "Cookie": f"JSESSIONID={self.jsessionid};",
            "Referer": "https://daisy.dsv.su.se/student/aktuellt.jspa"
        }

        response = requests.get(url, headers=STANDARD_HEADERS | headers)
        return "Log in" not in response.text

    def _is_staff_token_valid(self) -> bool:
        url = "https://daisy.dsv.su.se/servlet/schema.LokalSchema"
        headers = {
            "Cookie": f"JSESSIONID={self.staff_jsessionid};",
            "Referer": "https://daisy.dsv.su.se/anstalld/aktuellt.jspa"
        }

        response = requests.get(url, headers=STANDARD_HEADERS | headers)
        return "Log in" not in response.text

    def _add_booking_user(self, date: datetime.date):
        self._ensure_valid_jsessionid()
        url = "https://daisy.dsv.su.se/common/schema/bokning.jspa"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": f"JSESSIONID={self.jsessionid};"
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
            "searchTerm": self.search_term,
            "laggTillPersonID": self.lagg_till_person_id,
        }
        
        response = requests.post(url, headers=STANDARD_HEADERS | headers, data=data)
        return response

    def _get_raw_schedule_for_category(self, date: datetime.date, room_category: RoomCategory):
        if room_category == RoomCategory.BOOKABLE_GROUP_ROOMS:
            self._ensure_valid_jsessionid()
        else:
            self._ensure_valid_staff_jsessionid()
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
            "Cookie": f"JSESSIONID={self.jsessionid if room_category == RoomCategory.BOOKABLE_GROUP_ROOMS else self.staff_jsessionid};"
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

    def create_booking(self, date: datetime.date, from_time: RoomTime, to_time: RoomTime, room_category: RoomCategory, room_id: int, name: str, description: Optional[str] = None):
        if room_category == RoomCategory.BOOKABLE_GROUP_ROOMS:
            self._ensure_valid_jsessionid()
            # Bookable group rooms require a secondary participant to be added
            if not self.booking_user_added:
                self._add_booking_user(date)
                self.booking_user_added = True
        else:
            self._ensure_valid_staff_jsessionid()
        url = "https://daisy.dsv.su.se/common/schema/bokning.jspa"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": f"JSESSIONID={self.jsessionid};"
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

    def book_slots(self, room_category: RoomCategory, times: List[BookingSlot], date: datetime.date, title: str):
        for entry in times:
            # Book each room
            self.create_booking(
                date=date,
                from_time=entry.from_time,
                to_time=entry.to_time,
                room_category=room_category,
                room_id=entry.room.value,
                name=title,
                description=f"Booked via dsv-daisy-booker (https://github.com/Edwinexd/dsv-daisy-booker) at {datetime.datetime.now().isoformat()}"
            )

    def get_schedule_for_category(self, date: datetime.date, room_category: RoomCategory) -> Schedule:
        raw = self._get_raw_schedule_for_category(date, room_category)
        return parse_daisy_schedule(raw)
