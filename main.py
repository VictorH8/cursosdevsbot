from dotenv import load_dotenv
import os

from hydrogram import Client, filters
from hydrogram.enums import ChatMemberStatus
from hydrogram.types import (
    CallbackQuery,
    ChatPrivileges,
    Message,
    User,
)


from typing import Union, Optional, Callable
from functools import partial, wraps


load_dotenv()

cursosdevs = Client(
             api_id=os.environ['API_ID'],
             api_hash=os.environ['API_HASH'],
             bot_token=os.environ['BOT_TOKEN'],
             name='cursosdevs_bot',
             in_memory=True)

async def check_perms(
    message: Union[CallbackQuery, Message],
    permissions: Optional[ChatPrivileges] = None,
    complain_missing_perms: bool = True,
) -> bool:
    if isinstance(message, CallbackQuery):
        sender = partial(message.answer, show_alert=True)
        chat = message.message.chat
    else:
        sender = message.reply_text
        chat = message.chat
    # TODO: Cache all admin permissions in db.
    user = await chat.get_member(message.from_user.id)
    if user.status == ChatMemberStatus.OWNER:
        return True

    # No permissions specified, accept being an admin.
    if not permissions and user.status == ChatMemberStatus.ADMINISTRATOR:
        return True
    if user.status != ChatMemberStatus.ADMINISTRATOR:
        if complain_missing_perms:
            await sender("<b><i><u>Você não é um administrador</u></i></b>")
        return False

    missing_perms = [
        perm
        for perm, value in permissions.__dict__.items()
        if value and not getattr(user.privileges, perm)
    ]

    if not missing_perms:
        return True
    if complain_missing_perms:
        await sender("<b><i><u>Você não tem as seguintes permissões:</u></i></b>\n\n - <code>{permissions}</code>".format(permissions=", ".join(missing_perms)))
    return False

def require_admin(
    permissions: Optional[ChatPrivileges] = None,
    allow_in_private: bool = False,
    complain_missing_perms: bool = True,
):
    """Decorator that checks if the user is an admin in the chat.

    Parameters
    ----------
    permissions: ChatPrivileges
        The permissions to check for.
    allow_in_private: bool
        Whether to allow the command in private chats or not.
    complain_missing_perms: bool
        Whether to complain about missing permissions or not, otherwise the
        function will not be called and the user will not be notified.

    Returns
    -------
    Callable
        The decorated function.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, message: Union[CallbackQuery, Message], *args, **kwargs):
            if isinstance(message, CallbackQuery):
                sender = partial(message.answer, show_alert=True)
                msg = message.message
            elif isinstance(message, Message):
                sender = message.reply_text
                msg = message
            else:
                raise NotImplementedError(
                    f"require_admin can't process updates with the type '{message.__name__}' yet."
                )

            # We don't actually check private and channel chats.
            if msg.chat.type == ChatType.PRIVATE:
                if allow_in_private:
                    return await func(client, message, *args, *kwargs)
                return await sender("<i>Isso é apenas para grupos!!</i>")
            if msg.chat.type == ChatType.CHANNEL:
                return await func(client, message, *args, *kwargs)
            has_perms = await check_perms(message, permissions, complain_missing_perms)
            if has_perms:
                return await func(client, message, *args, *kwargs)
            return None

        return wrapper

    return decorator

async def get_target_user(c: cursosdevs, m: Message) -> User:
    if m.reply_to_message:
        return m.reply_to_message.from_user
    msg_entities = m.entities[1] if m.text.startswith("/") else m.entities[0]
    return await c.get_users(
        msg_entities.user.id
        if msg_entities.type == MessageEntityType.TEXT_MENTION
        else int(m.command[1])
        if m.command[1].isdecimal()
        else m.command[1]
    )

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
