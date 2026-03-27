import json
import re
from collections import Counter
from typing import Dict, List, Optional, Any
from pathlib import Path


class TextAnalyzer:


    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.text = ""
        self.stats = {}
        self._load_text()
    def _load_text(self) -> None:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.text = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {self.file_path}")
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла: {e}")

    def _clean_text(self) -> str:
        return re.sub(r'[^\w\s]', ' ', self.text)

    def _get_words(self) -> List[str]:
        cleaned_text = self._clean_text()
        words = cleaned_text.lower().split()
        return [word for word in words if word]

    def _get_chars(self) -> List[str]:
        chars = [char.lower() for char in self.text if char.isalpha()]
        return chars

    def analyze(self, filters: Optional[List[str]] = None) -> Dict[str, Any]:
        chars = self._get_chars()
        words = self._get_words()

        # Базовая статистика
        stats = {
            "general_stats": {
                "letters_count": len(self.text),
                "words_count": len(words)
            }
        }

        # Статистика по буквам
        if not filters or "letters" in filters or "all" in filters:
            char_counts = Counter(chars)
            if char_counts:
                sorted_chars = sorted(char_counts.values())
                median_idx = len(sorted_chars) // 2
                median_freq = sorted_chars[median_idx]

                # Находим букву, частота которой является медианной
                median_char = None
                for char, count in char_counts.items():
                    if count == median_freq:
                        median_char = char
                        break

                stats["letters_stats"] = {
                    "often": char_counts.most_common(1)[0],
                    "rare": char_counts.most_common()[-1],
                    "median": (median_char, median_freq),
                    "different_letter": len(char_counts)
                }

        # Статистика по словам
        if not filters or "words" in filters or "all" in filters:
            word_counts = Counter(words)
            if word_counts:

                min_count = min(word_counts.values())
                max_count = max(word_counts.values())

                words_with_min_count = [word for word, count in word_counts.items() if count == min_count]
                words_with_max_count = [word for word, count in word_counts.items() if count == max_count]

                stats["words_count"] = {
                    "min": min_count,
                    "max_count_letters": words_with_min_count[:15],  # Ограничиваем для читаемости
                    "max": max_count,
                    "min_count_letters": words_with_max_count[:15],  # Ограничиваем для читаемости
                    "unique_count": len(word_counts)
                }

        self.stats = stats
        return stats


