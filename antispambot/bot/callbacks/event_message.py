from aiogram.filters.callback_data import CallbackData


class BanMemberCallback(CallbackData, prefix='ban_member'):
    chat_id: int
    user_id: int


class UnbanMemberCallback(CallbackData, prefix='unban_member'):
    chat_id: int
    user_id: int


class AllowNicknameCallback(CallbackData, prefix='allow_nickname'):
    chat_id: int
    user_id: int


class DeleteMessageCallback(CallbackData, prefix='delete_message'):
    chat_id: int
    message_id: int
