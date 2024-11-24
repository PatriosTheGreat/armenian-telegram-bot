import enum
import datetime
import random

import word
import armenian_char

class UserConversationState(enum.IntEnum):
    NONE = 0
    TRAIN_LETTER = 1

class UserStatistics:
    def __init__(self):
        self.letter_to_learned = {}
        for char in armenian_char.alphabet:
            self.letter_to_learned[char] = 0

    def mark_letter_learned(self, letter: armenian_char.ArmenianChar):
        if letter in self.letter_to_learned:
            self.letter_to_learned[letter] += 1

    def choose_random_word(self) -> armenian_char.ArmenianChar:
        total_sum = sum(self.letter_to_learned.values())
        if total_sum == 0:
            return random.randint(0, len(armenian_char.alphabet) - 1)

        weights = [1 - x / total_sum for x in self.letter_to_learned.values()]
        return random.choices(range(len(armenian_char.alphabet)), weights=weights, k=1)[0]

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

    def asked_letter(self) -> armenian_char.ArmenianChar:
        return armenian_char.alphabet[self.asked_letter_id]

    def next_letter(self) -> armenian_char.ArmenianChar:
        self.letter_id += 1
        if self.letter_id >= len(armenian_char.alphabet):
            self.letter_id = 0
        return armenian_char.alphabet[self.letter_id]

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
