from dotenv import load_dotenv
import os

from hydrogram import Client, filters, enums


load_dotenv()

cursosdevs = Client(
             api_id=os.environ['API_ID'],
             api_hash=os.environ['API_HASH'],
             bot_token=os.environ['BOT_TOKEN'],
             name='cursosdevs_bot',
             in_memory=True)

@cursosdevs.on_message(filters.command('start',prefixes=['/','.','!']))
async def startando(client,message):
    await message.reply_text(f"<strong>online</strong>")



@cursosdevs.on_message(filters.command('id',prefixes=['/','.','!']))
async def idinfo(client,message):
    if enums.chat_type == "PRIVATE":
        await message.reply(f"ID: <strong>{message.user_id}</strong>\n")
    await message.reply(f"ID: <strong>{message.chat.id}</strong>\n")



@cursosdevs.on_message(filters.new_chat_members)
async def welcome(client,message):
    await cursosdevs.delete_messages(message.chat.id, message.id)
    await message.reply(f'Seja Bem Vindo Ao Nosso Grupo De Cursos Para Devs. @{message.from_user.username}')






@cursosdevs.on_message(filters.command('ban',prefixes=['/','.','!']))
async def banir(client,message):
    users = await cursosdevs.get_users(message.from_user.id)
    await cursosdevs.ban_chat_member(chat_id=message.chat.id,user_id=users.id)  



cursosdevs.run()
