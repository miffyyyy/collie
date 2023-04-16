import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import openai


load_dotenv(".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_BOT_KEY = os.getenv("DISCORD_BOT_KEY")

openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="", intents=intents)



@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_input = message.content

    system_message = {
        "role": "system",
        "content": f" "
    }

    user_message = {
        "role": "user",
        "content": f"{user_input}"
    }

    messages = [system_message, user_message]

    chat_response_user_answer = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    response_message = chat_response_user_answer.choices[0].message['content']

    await message.reply(response_message)

client.run(DISCORD_BOT_KEY)


