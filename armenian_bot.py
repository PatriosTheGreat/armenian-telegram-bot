import enum
import configparser
import logging
import random

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

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
    ArmenianChar('Եե', 'Э'),
    ArmenianChar('Զզ', 'З'),
    ArmenianChar('Իի', 'И'),
    ArmenianChar('Եե', 'Э'),
    ArmenianChar('Լլ', 'Л'),
    ArmenianChar('Խխ', 'Х'),
    ArmenianChar('Ծծ', 'Ц'),
    ArmenianChar('Կկ', 'К'),
    ArmenianChar('Հհ', 'Х'),
    ArmenianChar('Ձձ', 'Д'),
    ArmenianChar('Ղղ', 'Г'),
    ArmenianChar('Ճճ', 'Ч'),
    ArmenianChar('Մմ', 'М'),
    ArmenianChar('Յյ', 'Й'),
    ArmenianChar('Նն', 'Н'),
    ArmenianChar('Շշ', 'Ш'),
    ArmenianChar('Ոո', 'О'),
    ArmenianChar('Չչ', 'Ч'),
    ArmenianChar('Պպ', 'П'),
    ArmenianChar('Ջջ', 'Ж'),
    ArmenianChar('Ռռ', 'Р'),
    ArmenianChar('Սս', 'С'),
    ArmenianChar('Վվ', 'В'),
    ArmenianChar('Տտ', 'Т'),
    ArmenianChar('Րր', 'Р'),
    ArmenianChar('Ցց', 'Ц'),
    ArmenianChar('Ււ', 'У'),
    ArmenianChar('Փփ', 'Ф'),
    ArmenianChar('Քք', 'К'),
    ArmenianChar('Օօ', 'О'),
    ArmenianChar('Ֆֆ', 'Ф'),
    ArmenianChar('և', 'Ев')  # Союз "и"
]

class UserConversationState(enum.IntEnum):
    NONE = 0
    TRAIN_LETTER = 1

class UserInfo:
    def __init__(self):
        self.conversation_state = UserConversationState.NONE
        self.letter_id = -1
        self.asked_letter_id = 0

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
        user_id_to_info[chat_id] = UserInfo()

    return user_id_to_info[chat_id]

async def reset_my_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    get_user_info(update).conversation_state = UserConversationState.NONE
    await update.message.reply_text(f'Понял. Давай начнем все заного!')

async def learn_alphabet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    letter: ArmenianChar = get_user_info(update).next_letter()
    await update.message.reply_text(f'{letter.char}. {letter.description()}')


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

def main():
    """Run bot."""
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("learn_alphabet", learn_alphabet))
    app.add_handler(CommandHandler("reset_my_state", reset_my_state))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, conversation))
    app.run_polling()

if __name__ == '__main__':
    main()
