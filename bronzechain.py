''' Mostly AI generated. '''

import json
import asyncio
import logging
import argparse

import aiohttp

from telegram.ext import Application

# Set up logging.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class Bronzechain:
    # Message and email templates.
    MSG_1_TEXT = 'Respond with any message to confirm that you are well'
    MSG_2_TEXT = 'FINAL ATTEMPT: respond with any message to confirm that you are well'
    EMAIL_SUBJECT = '{} possibly incapacitated'
    EMAIL_BODY = '{} hasn\'t responded to wellness check messages sent {} hours ago.'
    
    def __init__(self, config_path):
        # Load configuration.
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.bot_token = config['bot_token']
        self.chat_id = config['chat_id']
        self.msg_1_deadline_sec = config['msg_1_deadline_hrs'] * 3600
        self.msg_2_deadline_sec = config['msg_2_deadline_hrs'] * 3600
        self.email_service_url = config['email_service_url']
        self.email_token = config['email_token']
        self.user_name = config['user_name']
        self.dest_email = config['dest_email']
        
        # Initialize Telegram bot.
        self.app = Application.builder().token(self.bot_token).build()
    
    async def send_message(self, text):
        ''' Send a message to the configured chat ID. '''

        message = await self.app.bot.send_message(chat_id=self.chat_id, text=text)
        return message.date
    
    async def get_last_msg(self):
        ''' Get the last message update from the bot or None if no valid message update. '''

        updates = await self.app.bot.get_updates(offset=-1, limit=1)
        if updates and updates[-1].message:
            return updates[-1]
        return None
    
    async def send_email(self, dest_email, subject, body):
        '''
        Send an email using a Pipedream pipeline. This allows us to forgo manual management
        of long-lived Gmail OAuth.
        '''

        headers = { 'Authorization': f'Bearer {self.email_token}' }
        body = {
            'dest_email': dest_email,
            'subject': subject,
            'body': body
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(self.email_service_url, data=body) as response:
              response.raise_for_status()
    
    async def run(self):
        ''' Run the main bot logic. '''

        try:
            # Send first message.
            logger.info('Sending first message...')
            msg_1_time = await self.send_message(self.MSG_1_TEXT)
            logger.info(f'First message sent at {msg_1_time}')
            
            # Wait for deadline.
            logger.info(f'Waiting for {self.msg_1_deadline_sec/3600} hours...')
            await asyncio.sleep(self.msg_1_deadline_sec)
            
            # Check for updates.
            logger.info('Checking for responses...')
            last_msg = await self.get_last_msg()
            
            # Check if there was a reply after the first message.
            if last_msg and last_msg.message.date > msg_1_time:
                logger.info('Received response after first message. Exiting.')
                return
            
            # Send second message.
            logger.info('No response received. Sending second message...')
            msg_2_time = await self.send_message(self.MSG_2_TEXT)
            logger.info(f'Second message sent at {msg_2_time}')
            
            # Wait for deadline.
            logger.info(f'Waiting for {self.msg_2_deadline_sec/3600} hours...')
            await asyncio.sleep(self.msg_2_deadline_sec)
            
            # Check for updates again.
            logger.info('Checking for responses...')
            last_msg = await self.get_last_msg()
            
            # Check if there was a reply after the second message.
            if last_msg and last_msg.message.date > msg_2_time:
                logger.info('Received response after second message. Exiting.')
                return
            
            # If we get here, no response was received after both messages.
            logger.info('No response received after both messages. Sending email notification...')
            
            # Send email notification.
            total_hours = int(round((self.msg_1_deadline_sec + self.msg_2_deadline_sec) / 3600))
            subject = self.EMAIL_SUBJECT.format(self.user_name)
            body = self.EMAIL_BODY.format(self.user_name, total_hours)
            await self.send_email(self.dest_email, subject, body)
            
        except Exception as e:
            logger.error(f'Error in bot execution: {str(e)}')
            await self.send_message(f'Error in bot execution:\n\t{str(e)}')

async def main():
    parser = argparse.ArgumentParser(description='Bronzechain')
    parser.add_argument('--config', type=str, default='bronzechain.json')
    args = parser.parse_args()
    
    bot = Bronzechain(args.config)
    await bot.run()

if __name__ == '__main__':
    asyncio.run(main())
