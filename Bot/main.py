import asyncio
from aiogram import Bot, Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from msg_handlers import r


async def main():
    dp = Dispatcher()
    dp.include_router(r)
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    bot = Bot(token=open("bot/TOKEN.txt").readline())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
