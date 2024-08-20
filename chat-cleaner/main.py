import os
import yaml
import warnings
from telethon import TelegramClient

# Suppress the specific warning about an already authorized session
warnings.filterwarnings("ignore", category=UserWarning, module="telethon.client.auth")

async def delete_my_messages_for_everyone(client: TelegramClient, data: dict):
    await client.start(data["phone_number"])
    
    # Verify the logged-in user
    me = await client.get_me()
    print(f"Nickname : {me.username}")
    print("########################################")
    print()
    print()
    
    # Get the user identity
    chat = await client.get_entity(data["chat_name"])
    uid  = me.id

    async for message in client.iter_messages(chat):
        if message.sender_id == uid:
            try:
                await client.delete_messages(chat, [message.id], revoke=True)
                print("-----------------------------------------")
                print(f"Message      : {message.id}")
                print(f"Message says : {message.text[:30]}")
                print(f"Message date : {message.date}")
                print("-----------------------------------------")
                print(f"Deleted my message for everyone with id: {message.id}")
            except Exception as e:
                print(f"Failed to delete message with id: {message.id} - {str(e)}")
    print("Done!")
    print("Bye!")
    print()
    return

def main():

    default = {
        "api_id":       "",
        "api_hash":     "",
        "phone_number": "",
        "chat_name":    ""
    }

    # If the config is not available, creata a new one
    if not os.path.exists("config.yaml"):
        with open("config.yaml", "w") as file:
            yaml.dump(default, file)
        
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)

    # Print config.yaml file
    print("########################################")
    print(f"API Id   : {data['api_id']}")
    print(f"API Hash : {data['api_hash']}")
    print(f"Tel Numb : {data['phone_number']}")
    print(f"Chat     : {data['chat_name']}")

    session_file = "default"

    try:
        client = TelegramClient(session_file, data["api_id"], data["api_hash"])
        client.loop.run_until_complete(delete_my_messages_for_everyone(client, data))
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

main()
