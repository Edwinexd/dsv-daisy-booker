import json
import os
from typing import List, Optional, Tuple, Union
import discord
from dotenv import load_dotenv

from agent import RoomRequest, handle_message
from daisy import Daisy
from scheduler import schedule_rooms
from schemas import BookingSlot, RoomCategory

load_dotenv()

OWNER_ID = int(os.getenv("DISCORD_OWNER_ID"))  # type: ignore
TOKEN: str = os.getenv("DISCORD_TOKEN")  # type: ignore

intents = discord.Intents.default()

client = discord.Client(intents=intents)

daisy = Daisy(
    os.getenv("SU_USERNAME"),
    os.getenv("SU_PASSWORD"),
    os.getenv("SECOND_USER_SEARCH_TERM"),
    int(os.getenv("SECOND_USER_ID")),
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
            title=f"{request[0].title if request[0].title is not None else 'Meeting'} - {request[0].date}",
            description="\n".join([f"{slot.room_name}: {slot.from_time.to_string()}->{slot.to_time.to_string()}" for slot in request[1]])
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
        daisy.book_slots(request[1], request[0].date, request[0].title if request[0].title is not None else 'Meeting')
        await interaction.followup.send("Slot(s) have been booked", ephemeral=True)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.active += 1
        await self.generate_and_set_embed(interaction=interaction)


cache = {}

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.author.id != OWNER_ID:
        return

    async with message.channel.typing():
        history = []
        prev_message = message.reference
        while prev_message is not None:
            ref = prev_message.cached_message
            if ref is None:
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
        for i in range(3):
            prompt = message.content
            try:
                print(history)
                response = handle_message(history, message.content)
                break
            except json.decoder.JSONDecodeError:
                history.append({"role": "user", "content": prompt})
                history.append({"role": "assistant", "content": "<invalid json>"})
                prompt = "<invalid json was provided try again next round>"
            if i == 2:
                await message.reply("I'm sorry, I'm having trouble understanding you")
                return
        requests = []
        for request in response[2]:
            schedule = daisy.get_schedule_for_category(request.date, RoomCategory.BOOKABLE_GROUP_ROOMS)
            requests.append((request, schedule_rooms(schedule, request.from_time, request.duration, request.breaks)))
        view = None
        if requests:
            view = Confirm(message.author, requests)
        print(response)
        sent = await message.reply(str(response[0]), view=view) # type: ignore
        if view is not None:
            await view.generate_and_set_embed(message=sent)
        cache[sent.id] = response[1]
        return


client.run(TOKEN)
