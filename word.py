class Word:
    def __init__(self, word: str, translation: str):
        self.word = word
        self.translation = translation

    def description(self) -> str:
        return f'{self.word}/{self.word.lower()} - {self.translation}'

class WordRepository:
    def get_word_starting_by(self, char) -> Word | None:
        for word in words:
            if word.word[0] == char.upper():
                return word
        return None

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
