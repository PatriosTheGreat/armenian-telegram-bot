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
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

### Read token
### ToDo: Extract to separate file
config = configparser.ConfigParser()
config.read('bot_config.ini')
token = config['DEFAULT']['BotToken']

class Word:
    def __init__(self, word, translation):
        self.word = word
        self.translation = translation

    def description(self) -> str:
        return f'{self.word}/{self.word.lower()} - {self.translation}'

words = [
    Word("Ամառ", "Лето"),
    Word("Բաներ", "Вещи"),
    Word("Գարուն", "Весна"),
    Word("Դիմակ", "Маска"),
    Word("Երգ", "Песня"),
    Word("Զվարճանալ", "Веселиться"),
    Word("Էջ", "Страница"),
    Word("Ընկեր", "Друг"),
    Word("Թռչուն", "Птица"),
    Word("Ժամանակ", "Время"),
    Word("Իսկ", "Но"),
    Word("Լույս", "Свет"),
    Word("Խաղ", "Игра"),
    Word("Ծառ", "Дерево"),
    Word("Կամուրջ", "Мост"),
    Word("Համալիր", "Комплекс"),
    Word("Ձյուն", "Снег"),
    Word("Ղազար", "Лазарь"),
    Word("Ճանապարհ", "Дорога"),
    Word("Մայր", "Мать"),
    Word("Յուրաքանչյուր", "Каждый"),
    Word("Նավ", "Корабль"),
    Word("Շնորհակալություն", "Спасибо"),
    Word("Որպես", "Как"),
    Word("Չարչարանք", "Страдание"),
    Word("Պահարանը", "Резерв"),
    Word("Ջուր", "Вода"),
    Word("Ռազմական", "Военный"),
    Word("Սիրելի", "Дорогой"),
    Word("Վարդ", "Роза"),
    Word("Տուն", "Дом"),
    Word("Րոպե", "Минута"),
    Word("Ցերեկ", "Дневное время"),
    Word("Փոքր", "Маленький"),
    Word("Քարտեր", "Карты"),
    Word("Օր", "День"),
    Word("Ֆուտբոլ", "Футбол"),
]

class WordRepository:
    def get_word_starting_by(self, char) -> Word | None:
        for word in words:
            if word.word[0] == char.upper():
                return word
        return None

wordRepo = WordRepository()

class ArmenianChar:
    def __init__(self, char, translation):
        self.char = char
        self.translation = translation

    def description(self) -> str:
        result = f'Буква {self.translation}.'
        sample_word = wordRepo.get_word_starting_by(self.char[0])
        if sample_word != None:
            result += '\nПример использования: ' + sample_word.description()

        return result


alphabet = [
    ArmenianChar('Աա', ['A']),
    ArmenianChar('Բբ', ['Б']),
    ArmenianChar('Գգ', ['Г']),
    ArmenianChar('Դդ', ['Д']),
    ArmenianChar('Եե', ['Е']),
    ArmenianChar('Զզ', ['З']),
    ArmenianChar('Էէ',['Э']),
    ArmenianChar('Ըը',['Ы']),
    ArmenianChar('Թթ',['Т']),
    ArmenianChar('Ժժ',['Ж']),
    ArmenianChar('Իի', ['И']),
    ArmenianChar('Լլ', ['Л']),
    ArmenianChar('Խխ', ['Х']),
    ArmenianChar('Ծծ', ['Ц']),
    ArmenianChar('Կկ', ['К']),
    ArmenianChar('Հհ', ['Х']),
    ArmenianChar('Ձձ', ['Дз']),
    ArmenianChar('Ղղ', ['Р']),
    ArmenianChar('Ճճ', ['Ч']),
    ArmenianChar('Մմ', ['М']),
    ArmenianChar('Յյ', ['Й']),
    ArmenianChar('Նն', ['Н']),
    ArmenianChar('Շշ', ['Ш']),
    ArmenianChar('Ոո', ['Во']),
    ArmenianChar('Չչ', ['Ч']),
    ArmenianChar('Պպ', ['П']),
    ArmenianChar('Ջջ', ['Дж']),
    ArmenianChar('Ռռ', ['Р']),
    ArmenianChar('Սս', ['С']),
    ArmenianChar('Վվ', ['В']),
    ArmenianChar('Տտ', ['Т']),
    ArmenianChar('Րր', ['Р']),
    ArmenianChar('Ցց', ['Ц']),
    ArmenianChar('Ււ/Ուու', ['В']),
    ArmenianChar('Փփ', ['П']),
    ArmenianChar('Քք', ['К']),
    ArmenianChar('Օօ', ['О']),
    ArmenianChar('Ֆֆ', ['Ф']),
]

class UserConversationState(enum.IntEnum):
    NONE = 0
    TRAIN_LETTER = 1

class UserStatistics:
    def __init__(self):
        self.letter_to_learned = {}

    def mark_letter_learned(self, letter: ArmenianChar):
        if letter in self.letter_to_learned:
            self.letter_to_learned[letter] += 1
        else:
            self.letter_to_learned[letter] = 1

class UserInfo:
    max_letter_attempts = 3

    def __init__(self, chat_id):
        self.conversation_state = UserConversationState.NONE
        self.letter_id = -1
        self.asked_letter_id = 0
        self.chat_id = chat_id
        self.is_subscribed = False
        self.last_conversation_trigger = datetime.datetime.now()
        self.attempts = 0
        self.stats = UserStatistics()

    def asked_letter(self) -> ArmenianChar:
        return alphabet[self.asked_letter_id]

    def next_letter(self) -> ArmenianChar:
        self.letter_id += 1
        if self.letter_id >= len(alphabet):
            self.letter_id = 0
        return alphabet[self.letter_id]

    def ask_random_letter(self) -> str:
        self.conversation_state = UserConversationState.TRAIN_LETTER
        self.attempts = 0
        self.asked_letter_id = random.randint(0, len(alphabet) - 1)
        return f'Что это за буква \'{self.asked_letter().char}\'?'
    
    def give_up(self) -> str:
        if self.conversation_state != UserConversationState.TRAIN_LETTER:
            return ""

        self.conversation_state = UserConversationState.NONE
        letter = self.asked_letter()
        return ('Ничего. В следующий раз угадаешь!' +
            f'\nЭто кстати была буква: {letter.description()}')

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
    user_info = get_user_info(update)
    await update.message.reply_text('Понял. Давай начнем все заного!\n' + user_info.give_up())

async def learn_next_char(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    letter: ArmenianChar = get_user_info(update).next_letter()
    await update.message.reply_text(f'{letter.char}. {letter.description()}')


async def learn_alphabet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = ''
    for letter in alphabet:
        result += f'{letter.char}. {letter.description()}\n\n'
    
    await update.message.reply_text(result)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_info = get_user_info(update)

    result = 'Ваша статистика:\n'
    for letter, amount in user_info.stats.letter_to_learned.items():
        result += f'Буква {letter.char}. Удачных отгадываний: {amount}\n'
    
    await update.message.reply_text(result)

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
        asked_letter: ArmenianChar = user_info.asked_letter()
        if user_letter in asked_letter.translation:
            user_info.stats.mark_letter_learned(asked_letter)
            reply_message = 'Бинго!\n' + user_info.ask_random_letter()
        elif user_info.attempts < UserInfo.max_letter_attempts:
            left_attempts = UserInfo.max_letter_attempts - user_info.attempts
            user_info.attempts += 1
            reply_message = f'Не угадал =(\nОсталось попыток: {left_attempts}.'
        else:
            reply_message = user_info.give_up()

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
