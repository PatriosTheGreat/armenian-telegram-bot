import asyncio
import datetime
import enum
import configparser
import logging
import random
import threading
import schedule

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

### Initialize logging subsystem
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

### Read token
### ToDo: Extract to separate file
config = configparser.ConfigParser()
config.read('bot_config.ini')
token = config['DEFAULT']['BotToken']

class ArmenianChar:
    def __init__(self, char, translate):
        self.char = char
        self.translate = translate

    def description(self) -> str:
        return f'Буква {self.translate}.'

alphabet = [
    ArmenianChar('Աա', 'A'),
    ArmenianChar('Բբ', 'Б'),
    ArmenianChar('Գգ', 'Г'),
    ArmenianChar('Դդ', 'Д'),
    ArmenianChar('Եե', 'Е'),
    ArmenianChar('Զզ', 'З'),
    ArmenianChar('Էէ','Э'),
    ArmenianChar('Ըը','Ы'),
    ArmenianChar('Թթ','Т'),
    ArmenianChar('Ժժ','Ж'),
    ArmenianChar('Իի', 'И'),
    ArmenianChar('Լլ', 'Л'),
    ArmenianChar('Խխ', 'Х'),
    ArmenianChar('Ծծ', 'Ц'),
    ArmenianChar('Կկ', 'К'),
    ArmenianChar('Հհ', 'Х'),
    ArmenianChar('Ձձ', 'Дз'),
    ArmenianChar('Ղղ', 'Р'),
    ArmenianChar('Ճճ', 'Ч'),
    ArmenianChar('Մմ', 'М'),
    ArmenianChar('Յյ', 'Й'),
    ArmenianChar('Նն', 'Н'),
    ArmenianChar('Շշ', 'Ш'),
    ArmenianChar('Ոո', 'Во'),
    ArmenianChar('Չչ', 'Ч'),
    ArmenianChar('Պպ', 'П'),
    ArmenianChar('Ջջ', 'Дж'),
    ArmenianChar('Ռռ', 'Р'),
    ArmenianChar('Սս', 'С'),
    ArmenianChar('Վվ', 'В'),
    ArmenianChar('Տտ', 'Т'),
    ArmenianChar('Րր', 'Р'),
    ArmenianChar('Ցց', 'Ц'),
    ArmenianChar('Ււ/Ուու', 'В'),
    ArmenianChar('Փփ', 'П'),
    ArmenianChar('Քք', 'К'),
    ArmenianChar('Օօ', 'О'),
    ArmenianChar('Ֆֆ', 'Ф'),
]

class UserConversationState(enum.IntEnum):
    NONE = 0
    TRAIN_LETTER = 1

class UserInfo:
    def __init__(self, chat_id):
        self.conversation_state = UserConversationState.NONE
        self.letter_id = -1
        self.asked_letter_id = 0
        self.chat_id = chat_id
        self.is_subscribed = False
        self.last_conversation_trigger = datetime.datetime.now()

    def asked_letter(self) -> ArmenianChar:
        return alphabet[self.asked_letter_id]

    def next_letter(self) -> ArmenianChar:
        self.letter_id += 1
        if self.letter_id >= len(alphabet):
            self.letter_id = 0
        return alphabet[self.letter_id]

    def ask_random_letter(self) -> str:
        self.conversation_state = UserConversationState.TRAIN_LETTER
        self.asked_letter_id = random.randint(0, len(alphabet) - 1)
        return f'Что это за буква \'{self.asked_letter().char}\'?'

# Which letter should user learn next
user_id_to_info = {}

async def help(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
"""Привет. Я бот который помогает практиковать армянский.
Просто начни со мной общаться и увидишь как все работает.""")

def get_user_info(update: Update) -> UserInfo:
    chat_id = update.message.chat.id
    if chat_id not in user_id_to_info:
        user_id_to_info[chat_id] = UserInfo(chat_id)

    return user_id_to_info[chat_id]

async def reset_my_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply = f'Понял. Давай начнем все заного!'
    user_info = get_user_info(update)
    if user_info.conversation_state == UserConversationState.TRAIN_LETTER:
        reply += f'\nЭто кстати была буква {user_info.asked_letter().char}'
    user_info.conversation_state = UserConversationState.NONE
    await update.message.reply_text(reply)

async def learn_alphabet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    letter: ArmenianChar = get_user_info(update).next_letter()
    await update.message.reply_text(f'{letter.char}. {letter.description()}')

async def subscribe_to_daily_train(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_info = get_user_info(update)
    user_info.is_subscribed = True
    user_info.last_conversation_trigger = datetime.datetime.now()
    await update.message.reply_text('Поздравля! Теперь я буду присылать тебе задания раз в день!')

async def unsubscribe_from_daily_train(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    get_user_info(update).is_subscribed = False
    await update.message.reply_text('Очень жаль что мы больше не друзья =(')

async def conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_info = get_user_info(update)

    reply_message: str
    if user_info.conversation_state == UserConversationState.NONE:
        reply_message = user_info.ask_random_letter()
    else:
        user_letter = update.message.text.strip().upper()
        if user_letter == user_info.asked_letter().translate:
            reply_message = 'Бинго!\n' + user_info.ask_random_letter()
            user_info.conversation_state = UserConversationState.TRAIN_LETTER
        else:
            reply_message = 'Не угадал =(\nПопробуй еще раз...'

    await update.message.reply_text(reply_message)


async def scheduled_conversation(app: Application):
    logging.info('Checking subscriptions')
    for (_, user_info) in user_id_to_info.items():
        now = datetime.datetime.now()
        total_diff = (now - user_info.last_conversation_trigger).total_seconds()
        logging.info(f'Checking user which is {user_info.is_subscribed}. Seconds since the last udate {total_diff}')
        if (user_info.is_subscribed and total_diff > 10):
            user_info.last_conversation_trigger = now
            await app.bot.send_message(chat_id=user_info.chat_id, text='Бу! Испугался? Не бойся, я друг, я тебя не обижу. Иди сюда, иди ко мне, сядь рядом со мной, посмотри мне в глаза. Ты видишь меня?')

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
    app.add_handler(CommandHandler("learn_alphabet", learn_alphabet))
    app.add_handler(CommandHandler("reset_my_state", reset_my_state))
    app.add_handler(CommandHandler("subscribe_to_daily_train", subscribe_to_daily_train))
    app.add_handler(CommandHandler("unsubscribe_from_daily_train", unsubscribe_from_daily_train))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, conversation))
    app.run_polling()

if __name__ == '__main__':
    main()
