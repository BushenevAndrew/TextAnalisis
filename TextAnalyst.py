import re
from collections import Counter
from typing import Dict, List, Optional, Any
from pathlib import Path


# Класс для анализа текстового файла: подсчёт статистики букв и слов.
class TextAnalyzer:
    # Инициализация анализатора текста.
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)  # Преобразуем путь в объект Path для удобства работы
        self.text = ""  # Хранит содержимое файла
        self.stats = {}  # Хранит результаты анализа
        self._load_text()  # Загружаем текст при инициализации

    # Загрузка текста из файла.
    def _load_text(self) -> None:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.text = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {self.file_path}")
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла: {e}")

    # Очистка текста: удаление всех символов, кроме букв и пробелов.
    def _clean_text(self) -> str:
        return re.sub(r'[^\w\s]', ' ', self.text)

    # Извлечение слов из текста (очищенных и приведённых к нижнему регистру).
    def _get_words(self) -> List[str]:
        cleaned_text = self._clean_text()
        words = cleaned_text.lower().split()
        return [word for word in words if word]  # Удаляем пустые строки

    # Извлечение всех букв из текста (приведённых к нижнему регистру).
    def _get_chars(self) -> List[str]:
        chars = [char.lower() for char in self.text if char.isalpha()]
        return chars

    # Анализ текста: подсчёт статистики букв и слов.
    def analyze(self, filters: Optional[List[str]] = None) -> Dict[str, Any]:
        chars = self._get_chars()
        words = self._get_words()

        stats = {
            "general_stats": {
                "letters_count": len(self.text),  # Общее количество символов в тексте
                "words_count": len(words)  # Общее количество слов
            }
        }

        if not filters or "letters" in filters or "all" in filters:
            if not chars:
                stats["letters_stats"] = {"error": "Нет букв для анализа"}
            else:
                char_counts = Counter(chars)  # Подсчёт частоты каждой буквы
                sorted_chars = sorted(char_counts.values())
                median_idx = (len(sorted_chars) - 1) // 2
                median_freq = sorted_chars[median_idx]
                median_char = None
                for char, count in char_counts.items():
                    if count == median_freq:
                        median_char = char
                        break

                stats["letters_stats"] = {
                    "often": char_counts.most_common(1)[0],  # Самая частая буква и её количество
                    "rare": char_counts.most_common()[-1],  # Самая редкая буква и её количество
                    "median": (median_char, median_freq),  # Медиана частоты букв
                    "different_letter": len(char_counts)  # Количество уникальных букв
                }

        if not filters or "words" in filters or "all" in filters:
            if not words:
                stats["words_stats"] = {"error": "Нет слов для анализа"}
            else:
                word_counts = Counter(words)  # Подсчёт частоты каждого слова
                min_count = min(word_counts.values())
                max_count = max(word_counts.values())

                words_with_min_count = [word for word, count in word_counts.items() if count == min_count]
                words_with_max_count = [word for word, count in word_counts.items() if count == max_count]

                stats["words_stats"] = {
                    "min_count": min_count,  # Минимальная частота слова
                    "words_with_min_count": words_with_min_count[:15],  # Список слов с минимальной частотой (до 15)
                    "max_count": max_count,  # Максимальная частота слова
                    "words_with_max_count": words_with_max_count[:15],  # Список слов с максимальной частотой (до 15)
                    "unique_count": len(word_counts)  # Количество уникальных слов
                }

        self.stats = stats
        return stats