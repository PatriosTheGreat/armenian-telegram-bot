import word

class Char:
    def __init__(self, char: str, translation: str):
        self.char: str = char
        self.translation: str = translation

def description(char: Char, word_repo: word.WordRepository) -> str:
    result = f'Буква {char.translation}.'
    sample_word = word_repo.get_word_starting_by(char.char[0])
    if sample_word != None:
        result += '\nПример использования: ' + sample_word.description()

    return result


class AlphabetRepository:
    alphabet = [
        Char('Աա', ['A']),
        Char('Բբ', ['Б']),
        Char('Գգ', ['Г']),
        Char('Դդ', ['Д']),
        Char('Եե', ['Е']),
        Char('Զզ', ['З']),
        Char('Էէ',['Э']),
        Char('Ըը',['Ы']),
        Char('Թթ',['Т']),
        Char('Ժժ',['Ж']),
        Char('Իի', ['И']),
        Char('Լլ', ['Л']),
        Char('Խխ', ['Х']),
        Char('Ծծ', ['Ц']),
        Char('Կկ', ['К']),
        Char('Հհ', ['Х']),
        Char('Ձձ', ['Дз']),
        Char('Ղղ', ['Р']),
        Char('Ճճ', ['Ч']),
        Char('Մմ', ['М']),
        Char('Յյ', ['Й']),
        Char('Նն', ['Н']),
        Char('Շշ', ['Ш']),
        Char('Ոո', ['Во']),
        Char('Չչ', ['Ч']),
        Char('Պպ', ['П']),
        Char('Ջջ', ['Дж']),
        Char('Ռռ', ['Р']),
        Char('Սս', ['С']),
        Char('Վվ', ['В']),
        Char('Տտ', ['Т']),
        Char('Րր', ['Р']),
        Char('Ցց', ['Ц']),
        Char('Ււ/Ուու', ['В']),
        Char('Փփ', ['П']),
        Char('Քք', ['К']),
        Char('Օօ', ['О']),
        Char('Ֆֆ', ['Ф']),
    ]

    def length(self) -> int:
        return len(AlphabetRepository.alphabet)

    def next_id(self, id: int) -> int:
        if id >= self.length():
            return 0
        return id + 1

    def get_char(self, id: int) -> Char:
        return AlphabetRepository.alphabet[id]
    
    def iterate(self):
        for letter in AlphabetRepository.alphabet:
            yield letter 