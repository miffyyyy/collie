### Collie
# Collie is a Discord bot that uses OpenAI's GPT-3.5-turbo to answer questions based on a pre-defined FAQ dataset. The bot searches for the best matching question in the FAQ dataset and uses the GPT-3.5-turbo model to generate a response to the user's query. If the bot cannot find a relevant answer in the FAQ, it will reply with "I don't know that".

## Features
- Uses BM25 for efficient question matching.
- Pre-processes user input to match with the FAQ dataset.
- Utilizes GPT-3.5-turbo to generate informative answers based on the FAQ dataset.
- Replies with "I don't know that" if it cannot find a suitable answer.

## Requirements
- Python 3.8 or higher
- An OpenAI API Key
- A Discord Bot Token

## Dependencies
- discord.py
- openai
- python-dotenv
- rank_bm25

