import asyncio
import datetime
import configparser
import logging
import threading
import schedule
import word
import armenian_char
import user_info

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

### Initialize logging subsystem
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

### Read token
### ToDo: Extract to separate file
config = configparser.ConfigParser()
config.read('bot_config.ini')
token = config['DEFAULT']['BotToken']

word_repo = word.WordRepository()
alphabet_repo = armenian_char.AlphabetRepository()

# Which letter should user learn next
user_id_to_info = {}

async def help(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
"""Привет. Я бот который помогает практиковать армянский.
Просто начни со мной общаться и увидишь как все работает.""")

def get_user_info(update: Update) -> user_info.UserInfo:
    chat_id = update.message.chat.id
    if chat_id not in user_id_to_info:
        user_id_to_info[chat_id] = user_info.UserInfo(chat_id, alphabet_repo)

    return user_id_to_info[chat_id]

async def reset_my_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    info = get_user_info(update)
    await update.message.reply_text('Понял. Давай начнем все заного!\n' + info.give_up(word_repo))

async def learn_next_char(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    letter: armenian_char.Char = get_user_info(update).next_letter()
    await update.message.reply_text(f'{letter.char}. {armenian_char.description(letter, word_repo)}')

async def learn_alphabet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = ''
    for letter in alphabet_repo.iterate():
        result += f'{letter.char}. {armenian_char.description(letter, word_repo)}\n\n'
    
    await update.message.reply_text(result)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    info = get_user_info(update)
    await update.message.reply_text(info.get_statistics())

async def subscribe_to_daily_train(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    info = get_user_info(update)
    info.is_subscribed = True
    info.last_conversation_trigger = datetime.datetime.now()
    await update.message.reply_text('Поздравля! Теперь я буду присылать тебе задания раз в день!')

async def unsubscribe_from_daily_train(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    get_user_info(update).is_subscribed = False
    await update.message.reply_text('Очень жаль что мы больше не друзья =(')

async def conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    info = get_user_info(update)
    user_message = update.message.text
    await update.message.reply_text(info.conversation(user_message))

async def scheduled_conversation(app: Application):
    logging.info('Checking subscriptions')
    for (_, info) in user_id_to_info.items():
        now = datetime.datetime.now()
        total_diff = (now - info.last_conversation_trigger).total_seconds()
        logging.info(f'Checking user which is {info.is_subscribed}. Seconds since the last udate {total_diff}')
        if (info.is_subscribed and total_diff > 10):
            info.last_conversation_trigger = now
            await app.bot.send_message(chat_id=info.chat_id, text='Бу! Испугался? Не бойся, я друг, я тебя не обижу. Иди сюда, иди ко мне, сядь рядом со мной, посмотри мне в глаза. Ты видишь меня?')

def schedule_sync(app: Application):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(scheduled_conversation(app))

def schedule_loop(app):
    schedule.every(10).seconds.do(lambda: schedule_sync(app))
    while True:
        schedule.run_pending()

def main():
    """Run bot."""
    app = ApplicationBuilder().token(token).build()

    schedule_thread = threading.Thread(target=schedule_loop, args=[app])
    schedule_thread.start()
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("learn_next_char", learn_next_char))
    app.add_handler(CommandHandler("learn_alphabet", learn_alphabet))
    app.add_handler(CommandHandler("reset_my_state", reset_my_state))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("subscribe_to_daily_train", subscribe_to_daily_train))
    app.add_handler(CommandHandler("unsubscribe_from_daily_train", unsubscribe_from_daily_train))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, conversation))
    app.run_polling()

if __name__ == '__main__':
    main()
