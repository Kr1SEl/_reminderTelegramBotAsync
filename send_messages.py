from telegram.ext import ContextTypes, Application
import asyncio
import os
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()

# application = (
#     Application.builder()
#     .token(os.getenv('TG_TOKEN'))
#     .build()
# )


# async def main():
#     await application.updater.bot.send_message(chat_id='5528046211', text='Hello')


# asyncio.run(main())


async def callback_minute(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id='5528046211', text='One message every minute')

application = Application.builder().token(os.getenv('TG_TOKEN')).build()
job_queue = application.job_queue

job_minute = job_queue.run_repeating(callback_minute, interval=60, first=10)

application.run_polling()
