"""Loading and representing quiz questions from the question pool."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

QUESTIONS_DIR = Path(
    os.path.expanduser("~/ownCloud/private/segeln/segelschein_d/theoretische")
)


@dataclass(frozen=True)
class Answer:
    text: str
    correct: bool


@dataclass(frozen=True)
class Question:
    category: str
    text: str
    answers: list[Answer]
    description: str | None = None

    @property
    def correct_answers(self) -> set[str]:
        return {a.text for a in self.answers if a.correct}


def _parse_file(path: Path) -> list[Question]:
    """Parse a JSON file with a top-level {"category": ..., "questions": [...]} object."""
    with path.open(encoding="utf-8") as f:
        obj = json.load(f)

    category = obj["category"]
    questions: list[Question] = []
    for q in obj["questions"]:
        answers = [Answer(text=a["text"], correct=bool(a["correct"])) for a in q["answers"]]
        questions.append(
            Question(
                category=category,
                text=q["question"],
                answers=answers,
                description=q.get("description"),
            )
        )

    return questions


def load_questions(base_dir: Path = QUESTIONS_DIR) -> list[Question]:
    """Recursively load all questions found under base_dir."""
    if not base_dir.is_dir():
        raise FileNotFoundError(f"Question pool directory not found: {base_dir}")

    questions: list[Question] = []
    for path in sorted(base_dir.rglob("*.json")):
        if not path.is_file():
            continue
        try:
            questions.extend(_parse_file(path))
        except (json.JSONDecodeError, KeyError, TypeError):
            # Skip files that aren't valid question files.
            continue

    return questions
