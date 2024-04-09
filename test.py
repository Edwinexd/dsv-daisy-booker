    

from daisy import RoomTime
from parse import parse_daisy_schedule
from scheduler import schedule


with open("Daisy » Schedule.html", "r", encoding="utf-8") as file:
    content = file.read()

rooms = parse_daisy_schedule(content)

# print(rooms)

# filter room["activities"] to only include rooms that begin with "G10"

print(schedule({room: slots for room, slots in rooms.activities.items() if room.startswith("G10")}, RoomTime.ELEVEN, 4, shift=True))
print(schedule({room: slots for room, slots in rooms.activities.items() if room.startswith("G10")}, RoomTime.TWENTY_TWO, 4, shift=True))
