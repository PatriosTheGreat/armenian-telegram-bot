import enum
import datetime
import random

import word
import armenian_char

class UserConversationState(enum.IntEnum):
    NONE = 0
    TRAIN_LETTER = 1

class UserStatistics:
    def __init__(self, alphabet: armenian_char.AlphabetRepository):
        self.alphabet = alphabet
        self.letter_to_learned = {}
        for letter in self.alphabet.iterate():
            self.letter_to_learned[letter] = 0

    def mark_letter_learned(self, letter: armenian_char.Char):
        if letter in self.letter_to_learned:
            self.letter_to_learned[letter] += 1

    def choose_random_word(self) -> armenian_char.Char:
        total_sum = sum(self.letter_to_learned.values())
        length = self.alphabet.length()
        if total_sum == 0:
            return random.randint(0, length - 1)

        weights = [1 - x / total_sum for x in self.letter_to_learned.values()]
        return random.choices(range(length), weights=weights, k=1)[0]

class UserInfo:
    max_letter_attempts = 3

    def __init__(self, chat_id, alphabet: armenian_char.AlphabetRepository):
        self.conversation_state = UserConversationState.NONE
        self.letter_id = -1
        self.asked_letter_id = 0
        self.chat_id = chat_id
        self.is_subscribed = False
        self.last_conversation_trigger = datetime.datetime.now()
        self.attempts = 0
        self.stats = UserStatistics(alphabet)
        self.alphabet = alphabet

    def asked_letter(self) -> armenian_char.Char:
        return self.alphabet.get_char(self.asked_letter_id)

    def next_letter(self) -> armenian_char.Char:
        self.letter_id = self.alphabet.next_id(self.letter_id)
        return self.alphabet.get_char(self.letter_id)

    def ask_random_letter(self) -> str:
        self.conversation_state = UserConversationState.TRAIN_LETTER
        self.attempts = 0

        self.asked_letter_id = self.stats.choose_random_word()
        return f'Что это за буква \'{self.asked_letter().char}\'?'
    
    def give_up(self, word_repo: word.WordRepository) -> str:
        if self.conversation_state != UserConversationState.TRAIN_LETTER:
            return ""

        self.conversation_state = UserConversationState.NONE
        letter = self.asked_letter()
        return ('Ничего. В следующий раз угадаешь!' +
            f'\nЭто кстати была буква: {armenian_char.description(letter, word_repo)}')
    
    def get_statistics(self) -> str:
        result = 'Ваша статистика:\n'
        for letter, amount in self.stats.letter_to_learned.items():
            if amount > 0:
                result += f'Буква {letter.char}. Удачных отгадываний: {amount}\n'
        return result

    def conversation(self, user_message: str) -> str:
        if self.conversation_state == UserConversationState.NONE:
            return self.ask_random_letter()
        else:
            asked_letter: armenian_char.Char = self.asked_letter()
            if user_message.strip().upper() in asked_letter.translation:
                self.stats.mark_letter_learned(asked_letter)
                return 'Бинго!\n' + self.ask_random_letter()
            elif self.attempts < UserInfo.max_letter_attempts:
                left_attempts = UserInfo.max_letter_attempts - self.attempts
                self.attempts += 1
                return f'Не угадал =(\nОсталось попыток: {left_attempts}.'
            else:
                return self.give_up(self.word_repo)
