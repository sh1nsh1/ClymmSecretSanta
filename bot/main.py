import asyncio
from aiogram import Bot, Dispatcher, types
from msg_handlers import r

dp = Dispatcher()
dp.include_router(r)
bot = Bot(token="6365079135:AAF4hUcftH44fBRsb4V8JcoicsOlw7lWzMs")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# @dp.message()
# async def e(message:types.Message):
#     await bot.send_contact(message.chat.id, message)

if __name__ == "__main__":
    asyncio.run(main())
