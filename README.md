# Bronzechain

Bronzechain is a script that sends alerts via Telegram and follows up with an email notification if no response is received.

## Instructions

- Install Pip packages `python-telegram-bot` and `aiohttp`.

- Create a Telegram bot, start a conversation with the end user, and note down the bot's token and the conversation ID.

- Set up a Pipedream workflow that accepts information as sent by this script and sends an email.

- Update `bronzechain.json` to contain your Telegram bot's token, Telegram conversation ID, workflow information, destination email addresses and other configuration.

- Schedule executions of `python3 bronzechain.py` as desired.
