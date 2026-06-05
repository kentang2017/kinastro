from __future__ import annotations

import json
from pathlib import Path
from typing import Any

questions = [
    "Shall I obtain my wish?",
    "Shall I have success in my undertakings?",
    "Shall I gain or lose in my cause?",
    "Shall I have to live in foreign parts?",
    "Will the Stranger return from abroad?",
    "Shall I recover my property stolen?",
    "Will my friend be true in his dealings?",
    "Shall I have to travel?",
    "Does the person love and regard me?",
    "Will the marriage be prosperous?",
    "What sort of a wife or husband shall I have?",
    "Will she have a son or a daughter?",
    "Will the Patient recover from his illness?",
    "Will the Prisoner be released?",
    "Shall I be lucky or unlucky this day?",
    "What does my dream signify?",
]

questions_zh = [
    "我能如願以償嗎？",
    "我的事業與計畫會成功嗎？",
    "我的這件事情會得利還是失利？",
    "我會在異鄉生活嗎？",
    "那位遠行者會從海外歸來嗎？",
    "我能找回被盜的財物嗎？",
    "我的朋友在往來中會真誠可靠嗎？",
    "我將要出行旅行嗎？",
    "那個人愛我、重視我嗎？",
    "這段婚姻會幸福順遂嗎？",
    "我會有怎樣的妻子或丈夫？",
    "她會生兒子還是女兒？",
    "病人會從這場病中康復嗎？",
    "囚犯會被釋放嗎？",
    "我今天是幸運還是不幸？",
    "我的夢象徵著什麼？",
]

question_pairs = [
    {"en": en, "zh": zh}
    for en, zh in zip(questions, questions_zh)
]

oraculum = [
    ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q"],
    ["B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "Ɐ"],
    ["C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "A", "B"],
    ["D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "A", "B", "C"],
    ["E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "A", "B", "C", "D"],
    ["F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "A", "B", "C", "D", "E"],
    ["G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "A", "B", "C", "D", "E", "F"],
    ["H", "I", "K", "L", "M", "N", "O", "P", "Q", "A", "B", "C", "D", "E", "F", "G"],
    ["I", "K", "L", "M", "N", "O", "P", "Q", "A", "B", "C", "D", "E", "F", "G", "H"],
    ["K", "L", "M", "N", "O", "P", "Q", "A", "B", "C", "D", "E", "F", "G", "H", "I"],
    ["L", "M", "N", "O", "P", "Q", "A", "B", "C", "D", "E", "F", "G", "H", "I", "K"],
    ["M", "N", "O", "P", "Q", "A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L"],
    ["N", "O", "P", "Q", "A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M"],
    ["O", "P", "Q", "A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N"],
    ["P", "Q", "A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O"],
    ["Q", "A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P"],
]
ORACULUM_LETTERS = sorted({symbol for row in oraculum for symbol in row})

_answers_path = Path(__file__).with_name("answers.json")
try:
    with _answers_path.open(encoding="utf-8") as _f:
        answers: dict[str, list[str]] = json.load(_f)
except FileNotFoundError as exc:  # pragma: no cover - runtime packaging safety
    raise RuntimeError(
        f"Napoleon Oraculum answers.json not found at {_answers_path}. "
        "Verify the package installation is complete."
    ) from exc
except json.JSONDecodeError as exc:  # pragma: no cover - runtime packaging safety
    raise RuntimeError(
        f"Napoleon Oraculum answers.json contains invalid JSON at {_answers_path}. "
        "The file may be corrupted; consider reinstalling the package."
    ) from exc

def get_oraculum_answer(question_index: int, number_index: int) -> dict[str, Any]:
    """Resolve letter and answer by question index and 0-based number index."""
    if not (0 <= question_index < 16):
        raise ValueError("question_index must be in 0..15")
    if not (0 <= number_index < 16):
        raise ValueError("number_index must be in 0..15")

    letter = oraculum[question_index][number_index]
    letter_answers = answers.get(letter)
    if not letter_answers:
        raise KeyError(f"No answers table for letter: {letter}")

    return {
        "question_en": questions[question_index],
        "question_zh": questions_zh[question_index],
        "question_index": question_index,
        "number": number_index + 1,
        "letter": letter,
        "answer": letter_answers[number_index],
    }
