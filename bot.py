import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
import openai
from rank_bm25 import BM25Okapi
import numpy as np

load_dotenv(".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_BOT_KEY = os.getenv("DISCORD_BOT_KEY")

openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="", intents=intents)
token_names = ["ETH", "BTC", "DAI"]


def preprocess_text(text, tokens):
    for token in tokens:
        text = text.replace(token, "{T}")
    return text.lower()


def detect_token_name(text, tokens):
    for token in tokens:
        if token in text:
            return token
    return None


with open("snapshot-faq.json") as f:
    faq_data = json.load(f)

preprocessed_corpus = [preprocess_text(item["question"], token_names) for item in faq_data["data"]]
bm25 = BM25Okapi(preprocessed_corpus)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    user_input = message.content
    print("userInput:", user_input)

    # Preprocess the user input
    preprocessed_input = preprocess_text(user_input, token_names)

    # Use the preprocessed input for matching with the BM25 algorithm
    scores = bm25.get_scores(preprocessed_input)
    best_match_index = np.argmax(scores)
    best_matching_faq = faq_data["data"][best_match_index]
    question = best_matching_faq["question"]
    answer = best_matching_faq["answer"]

    try:
        if max(scores) > 2.0:
            response_message = answer
        else:
            system_message = {
                "role": "system",
                "content": f"You are a helpful FAQ bot for the Snapshot (decentralized governance) support channel. "
                           f"You should only reply to questions (not statements) and can only respond in two ways, "
                           f"1. Answer the user's question using the information from the best-matching FAQ"
                           f"  2. If cannot find a relevant answer to the provided question or "
                           f"when the question is unclear, ambiguous, or incomplete then reply 'I don't know that'. "
                           f"Under no circumstances should you response with your own made up answers. "
                            f"Here is the best matching FAQ: "
                           f"Q: {question}\nA: {answer}"
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


        if "I don't know that" in response_message:
            if not os.path.exists("snapshot-faq-unknown.json"):
                with open("snapshot-faq-unknown.json", "w") as f:
                    json.dump([], f)

            # Read the existing file_array
            with open("snapshot-faq-unknown.json", "r") as f:
                file_array = json.load(f)

            if not any(el["content"] == user_input for el in file_array):
                file_array.append({"count": 0, "content": user_input})
            else:
                index = next(i for i, el in enumerate(file_array) if el["content"] == user_input)
                file_array[index]["count"] += 1
            unique_file_array = list({v["content"]: v for v in file_array}.values())

            with open("snapshot-faq-unknown.json", "w") as f:
                json.dump(unique_file_array, f, indent=2)

    except Exception as error:
        print(error)
client.run(DISCORD_BOT_KEY)


