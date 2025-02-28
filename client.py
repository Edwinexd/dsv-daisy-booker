"""
A discord bot capable of booking student group rooms and staff rooms via Daisy (administration tool for Department of Computer and Systems Sciences at Stockholm University)
Copyright (C) 2024 Edwin Sundberg

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import os
from typing import List, Optional, Tuple, Union
import discord
from dotenv import load_dotenv

from agent import RoomRequest, handle_message_retries
from daisy import BookingError, Daisy
from scheduler import schedule_rooms
from schemas import BookingSlot, RoomCategory
from utils import run_async

load_dotenv()

OWNER_ID = int(os.getenv("DISCORD_OWNER_ID"))  # type: ignore
TOKEN: str = os.getenv("DISCORD_TOKEN")  # type: ignore

intents = discord.Intents.default()

client = discord.Client(intents=intents)

daisy = Daisy(
    os.getenv("SU_USERNAME"), # type: ignore
    os.getenv("SU_PASSWORD"), # type: ignore
    os.getenv("SECOND_USER_SEARCH_TERM"), # type: ignore
    int(os.getenv("SECOND_USER_ID")), # type: ignore
    staff = bool(int(os.getenv("SU_STAFF", "0"))), # type: ignore
)

# Discord UI element (YES/NO) with BookingSlot
class Confirm(discord.ui.View):
    def __init__(self, author: Union[discord.User, discord.Member], requests: List[Tuple[RoomRequest, List[BookingSlot]]]) -> None:
        super().__init__()
        self.author = author
        self.requests = requests
        self.active = 0

    async def generate_and_set_embed(self, message: Optional[discord.Message] = None, interaction: Optional[discord.Interaction] = None):
        if message is None and interaction is None:
            raise ValueError("Either message or interaction must be provided")
        if self.active >= len(self.requests):
            embed = discord.Embed(title="All slots have been processed")
            if message is not None:
                await message.edit(embed=embed, view=None)
            elif interaction is not None:
                await interaction.response.edit_message(embed=embed, view=None)
            self.stop()
            return
        request = self.requests[self.active]
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title=f"{request[0].room_category}: {request[0].title if request[0].title is not None else 'Meeting'} - {request[0].date}",
            description="\n".join([f"{slot.room.name}: {slot.from_time.to_string()}->{slot.to_time.to_string()}" for slot in request[1]])
        )
        embed.set_footer(text=f"Request: {self.active + 1}/{len(self.requests)}")
        if message is not None:
            await message.edit(embed=embed)
        elif interaction is not None:
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Book", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.active += 1
        await self.generate_and_set_embed(interaction=interaction)
        request = self.requests[self.active-1]
        try:
            await run_async(daisy.book_slots, request[0].room_category, request[1], request[0].date, request[0].title if request[0].title is not None else 'Meeting')
        except BookingError as e:
            await interaction.followup.send(f"Failed to book slot(s): {e}", ephemeral=True)
        else:
            await interaction.followup.send("Slot(s) have been booked", ephemeral=True)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.active += 1
        await self.generate_and_set_embed(interaction=interaction)


cache = {} # Memory leaks but for the scope of the project, it's fine

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.author.id != OWNER_ID:
        return

    if not message.content:
        return

    async with message.channel.typing():
        history = []
        prev_message = message.reference
        while prev_message is not None:
            ref = prev_message.cached_message
            if ref is None:
                if prev_message.message_id is None:
                    break
                ref = await message.channel.fetch_message(prev_message.message_id)
            if ref.author.id == client.user.id: # type: ignore
                history.append(
                    {
                        "role": "assistant",
                        "content": json.dumps({"conversations_response": ref.content, "requests": cache.get(ref.id, [])}),
                    }
                )
            else:
                history.append({"role": "user", "content": ref.content})
            prev_message = ref.reference
        history.reverse()
        try:
            response = await run_async(handle_message_retries, history, message.content, staff=daisy.staff)
        except (json.decoder.JSONDecodeError, ValueError):
            await message.reply("I'm sorry, I'm having trouble understanding you")
            return
        requests = []
        for request in response[2]:
            schedule = await run_async(daisy.get_schedule_for_category, request.date, request.room_category)
            requests.append((request, schedule_rooms(schedule, request.from_time, request.duration, request.breaks, request.room_restrictions)))
        view = None
        if requests:
            view = Confirm(message.author, requests)
        sent = await message.reply(str(response[0]), view=view) # type: ignore
        if view is not None:
            await view.generate_and_set_embed(message=sent)
        cache[sent.id] = response[1]
        return


if __name__ == "__main__":
    client.run(TOKEN)
