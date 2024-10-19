import asyncio
import logging
import sys

from antispambot.bot.factory import create_bot, create_dispatcher


async def main(bot_token: str) -> None:
    bot = create_bot(bot_token)
    await bot.delete_webhook(drop_pending_updates=True)
    dispatcher = create_dispatcher()
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python main.py <BOT_TOKEN> [--debug-log]')
        exit(1)

    BOT_TOKEN = sys.argv[1]

    if '--debug-log' in sys.argv:
        logging.basicConfig(
            filename='logs.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            filename='logs.log',
            format='%(asctime)s - %(levelname)s - %(message)s',
        )
        logging.getLogger('aiogram').setLevel(logging.WARNING)

    asyncio.run(main(BOT_TOKEN))
