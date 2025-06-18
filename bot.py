import asyncio
import random
from telethon import TelegramClient

# Shared API ID and API Hash for all accounts
api_id = 24561470  # Replace with your own API ID
api_hash = '1e2d3c0c1fd09ae41a710d2daea8374b'  # Replace with your own API Hash

# List of phone numbers for different accounts
phone_numbers = [
    "+918502921793",
    # Replace with another phone number
    # Add more phone numbers as needed
]

# ID of the Telegram group to send notifications to
NOTIFICATION_GROUP_ID = --1002879398599  # Replace with your Telegram group ID (must be an integer)

# Generate account configurations based on the list of phone numbers
accounts_config = [
    {"api_id": api_id, "api_hash": api_hash, "phone_number": phone_number}
    for phone_number in phone_numbers
]

class Account:
    def __init__(self, api_id, api_hash, phone_number):
        self.phone_number = phone_number
        self.session_file = f'session_{phone_number}.session'
        self.client = TelegramClient(self.session_file, api_id, api_hash)
        self.stop_hunting = False

    async def start_hunting(self):
        async with self.client:
            try:
                bot_entity = await self.client.get_entity('@HeXamonbot')
                while not self.stop_hunting:
                    # Fetch the last 2 messages from the bot
                    last_messages = []
                    async for message in self.client.iter_messages(bot_entity, limit=2):
                        last_messages.append(message)

                    # Check if "✨ Shiny Pokémon found!" is in any of the messages
                    shiny_found = any('✨ Shiny Pokémon found!' in message.message for message in last_messages)
                    if shiny_found:
                        self.stop_hunting = True
                        print(f'Shiny Pokémon found! Stopping the bot for {self.session_file}...')
                        # Notify the group
                        await self.notify_group()
                        break

                    # Check if daily limit is reached
                    limit_reached = any('Daily hunt limit reached' in message.message for message in last_messages)
                    if limit_reached:
                        self.stop_hunting = True
                        print(f'Daily hunt limit reached! Stopping the bot for {self.session_file}...')
                        await self.client.disconnect()
                        break

                    # Process the messages
                    for message in last_messages:
                        await self.handle_message(message)

                    # Continue hunting if not stopped
                    if not self.stop_hunting:
                        await self.client.send_message('@HeXamonbot', '/hunt')

                    # Random delay between hunts
                    gap = random.randint(2, 6)
                    await asyncio.sleep(gap)
            except Exception as e:
                print(f"An error occurred in start_hunting for {self.session_file}: {e}")
            finally:
                if self.client.is_connected:
                    await self.client.disconnect()

    async def handle_message(self, message):
        # List of keywords to stop the hunting
        stop_keywords = [
            "✨ Shiny Pokémon found!",
            "Daily hunt limit reached"
        ]
        # Check if any stopping keyword is in the message
        if any(keyword in message.message for keyword in stop_keywords):
            self.stop_hunting = True
            print(f"Stopping hunting for {self.session_file} due to message: {message.message}")
        else:
            print(f"Received message for {self.session_file}: {message.message}")

    async def notify_group(self):
        # Notify the Telegram group
        try:
            await self.client.send_message(NOTIFICATION_GROUP_ID, "Shiny aaya h account dekho")
            print(f"Notification sent to group {NOTIFICATION_GROUP_ID} from {self.session_file}.")
        except Exception as e:
            print(f"Error sending notification to group {NOTIFICATION_GROUP_ID} from {self.session_file}: {e}")

    async def connect(self):
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                await self.client.send_code_request(self.phone_number)
                # You'll need to manually input the code here when the script runs for the first time
                code = input(f'Enter the code for {self.phone_number}: ')
                await self.client.sign_in(self.phone_number, code)
            print(f"Account {self.session_file} connected.")
        except Exception as e:
            print(f"Could not connect account {self.session_file}: {e}")
            return False
        return True

    def close(self):
        self.stop_hunting = True
        if self.client.is_connected:
            self.client.disconnect()
        print(f"Hunting stopped and client disconnected for {self.session_file}.")

async def start_hunting_for_all_accounts(accounts):
    tasks = []
    connected_accounts = []
    for config in accounts:
        account = Account(config["api_id"], config["api_hash"], config["phone_number"])
        if await account.connect():
            connected_accounts.append(account)
            task = asyncio.create_task(account.start_hunting())
            tasks.append(task)
        else:
            print(f"Skipping hunting for {account.session_file} due to connection failure.")

    # Wait for all tasks to complete
    await asyncio.gather(*tasks)

    # Close all account connections
    for account in connected_accounts:
        account.close()

    print("All active accounts have stopped hunting and disconnected.")

async def main():
    await start_hunting_for_all_accounts(accounts_config)

if __name__ == "__main__":
    asyncio.run(main())
                      
