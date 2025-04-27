# Bronzechain

Bronzechain is a script that sends alerts via Telegram and follows up with an email notification if no response is received.

## Instructions

- Install the following Pip packages: `google-api-python-client`, `google-auth-httplib2`,  `google-auth-oauthlib` and `python-telegram-bot`.

- Create a Telegram bot, start a conversation with the end user, and note down the bot's token and the conversation ID.

- Follow the Google workspace [documentation](https://developers.google.com/workspace/gmail/api/quickstart/python) for authorising and running the quickstart example.

- Modify the example to include the `https://www.googleapis.com/auth/gmail.send` scope and execute it. Copy the generated `token.json` into this project's folder.

- Update `bronzechain.json` to contain your Telegram bot's token, Telegram conversation ID, source and destination email addresses and other configuration.

- Schedule executions of `python3 bronzechain.py` as desired.
