import asyncio
import logging
from os import getenv
import sys

from antispambot.bot.factory import create_bot, create_dispatcher


async def main(bot_token: str) -> None:
    bot = create_bot(bot_token)
    await bot.delete_webhook(drop_pending_updates=True)
    dispatcher = create_dispatcher()
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    if '--debug-log' in sys.argv:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    BOT_TOKEN = getenv('BOT_TOKEN')
    assert BOT_TOKEN
    asyncio.run(main(BOT_TOKEN))
