import datetime
import os 
import dotenv

from daisy import Daisy
from login import daisy_login
from schemas import RoomCategory

dotenv.load_dotenv()

daisy = Daisy(
    os.getenv("SU_USERNAME"), # type: ignore
    os.getenv("SU_PASSWORD"), # type: ignore
    os.getenv("SECOND_USER_SEARCH_TERM"), # type: ignore
    int(os.getenv("SECOND_USER_ID")), # type: ignore
    staff = bool(int(os.getenv("SU_STAFF", "0"))), # type: ignore
)

print(daisy._ensure_valid_staff_jsessionid())

print(daisy._is_staff_token_valid())

print(daisy.get_schedule_for_category(datetime.date.today(), RoomCategory.SEMINAR_ROOMS))
