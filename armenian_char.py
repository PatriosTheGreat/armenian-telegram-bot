import word

class ArmenianChar:
    def __init__(self, char: str, translation: str):
        self.char: str = char
        self.translation: str = translation

def description(char: ArmenianChar, word_repo: word.WordRepository) -> str:
    result = f'Буква {char.translation}.'
    sample_word = word_repo.get_word_starting_by(char.char[0])
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
