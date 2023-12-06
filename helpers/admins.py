from typing import Union
from functools import partial

from hydrogram.enums import ChatMemberStatus

from pyrogram.types import (
    CallbackQuery,
    ChatPrivileges,
    Message,
    User,
)


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
            has_perms = await check_perms(message, permissions, complain_missing_perms, strings)
            if has_perms:
                return await func(client, message, *args, *kwargs)
            return None

        return wrapper

    return decorator
