"""Segel D theory exam trainer - PySide6 GUI quiz app."""

from __future__ import annotations

import random
import sys

from pathlib import Path

import qdarkstyle
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QMovie, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from questions import Question, load_questions

GIF_BAD_PATH = Path(__file__).resolve().parent / "bad.gif"
GIF_GOOD_PATH = Path(__file__).resolve().parent / "good.gif"
WRONG_THRESHOLD = 15
QUESTION_LIMIT = 60

NEUTRAL_STYLE = "QFrame#answerRow { background-color: transparent; border-radius: 6px; }\nQCheckBox { spacing: 12px; }\nQCheckBox::indicator { width: 28px; height: 28px; }"
CORRECT_STYLE = "QFrame#answerRow { background-color: #2e7d32; border-radius: 6px; }\nQCheckBox { spacing: 12px; }\nQCheckBox::indicator { width: 28px; height: 28px; }"
WRONG_STYLE = "QFrame#answerRow { background-color: #b71c1c; border-radius: 6px; }\nQCheckBox { spacing: 12px; }\nQCheckBox::indicator { width: 28px; height: 28px; }"


class AnswerRow(QFrame):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.setObjectName("answerRow")
        self.setStyleSheet(NEUTRAL_STYLE)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)

        self.checkbox = QCheckBox()
        layout.addWidget(self.checkbox)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.mousePressEvent = lambda _event: self.checkbox.toggle()
        layout.addWidget(self.label, stretch=1)

    def set_font(self, font: QFont) -> None:
        self.label.setFont(font)

    def set_state(self, correct: bool | None) -> None:
        if correct is None:
            self.setStyleSheet(NEUTRAL_STYLE)
        elif correct:
            self.setStyleSheet(CORRECT_STYLE)
        else:
            self.setStyleSheet(WRONG_STYLE)

    def is_checked(self) -> bool:
        return self.checkbox.isChecked()


class QuizWindow(QWidget):
    def __init__(self, questions: list[Question]) -> None:
        super().__init__()
        self.setWindowTitle("Segelschein D - Theorie Training")
        self.resize(750, 750)

        self.questions = questions
        self.correct_count = 0
        self.wrong_count = 0
        self.answered_count = 0
        self.current: Question | None = None
        self.answer_rows: list[AnswerRow] = []
        self.answered = False
        self.result_shown = False

        self._build_ui()
        self._next_question()

    def _build_ui(self) -> None:
        title_font = QFont("Segoe UI", 13, QFont.Weight.Bold)
        question_font = QFont("Segoe UI", 15)
        score_font = QFont("Segoe UI", 11)
        answer_font = QFont("Segoe UI", 12)
        description_font = QFont("Segoe UI", 10)
        button_font = QFont("Segoe UI", 11, QFont.Weight.DemiBold)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        top_row = QHBoxLayout()
        self.category_label = QLabel()
        self.category_label.setFont(title_font)
        top_row.addWidget(self.category_label)
        top_row.addStretch()
        self.score_label = QLabel()
        self.score_label.setFont(score_font)
        top_row.addWidget(self.score_label)
        root.addLayout(top_row)

        self.question_label = QLabel()
        self.question_label.setFont(question_font)
        self.question_label.setWordWrap(True)
        root.addWidget(self.question_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setVisible(False)
        root.addWidget(self.image_label)

        self.answers_layout = QVBoxLayout()
        self.answers_layout.setSpacing(8)
        root.addLayout(self.answers_layout)

        self.description_label = QLabel()
        self.description_label.setFont(description_font)
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #9aa0a6;")
        root.addWidget(self.description_label)
        root.addStretch()

        self.answer_font = answer_font

        button_row = QHBoxLayout()
        self.submit_button = QPushButton("Prüfen")
        self.submit_button.setFont(button_font)
        self.submit_button.setMinimumHeight(50)
        self.submit_button.setMinimumWidth(160)
        self.submit_button.clicked.connect(self._check_answer)
        button_row.addWidget(self.submit_button)

        self.next_button = QPushButton("Nächste Frage")
        self.next_button.setFont(button_font)
        self.next_button.setMinimumHeight(50)
        self.next_button.setMinimumWidth(200)
        self.next_button.clicked.connect(self._next_question)
        button_row.addWidget(self.next_button)
        button_row.addStretch()

        root.addLayout(button_row)

    def _update_score_label(self) -> None:
        self.score_label.setText(
            f"Richtig: {self.correct_count}  |  Falsch: {self.wrong_count}  |  Fragen: {self.answered_count}"
        )

    def _clear_answers(self) -> None:
        while self.answers_layout.count():
            item = self.answers_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.answer_rows = []

    def _next_question(self) -> None:
        self.current = random.choice(self.questions)
        self.answered = False
        self.submit_button.setEnabled(True)

        self.category_label.setText(self.current.category)
        self.question_label.setText(self.current.text)
        self.description_label.setText("")
        self._update_score_label()
        self._update_image()

        self._clear_answers()
        for answer in self.current.answers:
            row = AnswerRow(answer.text)
            row.set_font(self.answer_font)
            self.answers_layout.addWidget(row)
            self.answer_rows.append(row)

    def _update_image(self) -> None:
        if self.current is not None and self.current.image is not None and self.current.image.is_file():
            pixmap = QPixmap(str(self.current.image))
            if not pixmap.isNull():
                scaled = pixmap.scaledToWidth(600, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(scaled)
                self.image_label.setVisible(True)
                return
        self.image_label.clear()
        self.image_label.setVisible(False)

    def _check_answer(self) -> None:
        if self.answered or self.current is None:
            return
        self.answered = True
        self.submit_button.setEnabled(False)

        all_correct = True
        wrong_this_question = 0
        for answer, row in zip(self.current.answers, self.answer_rows):
            row.checkbox.setEnabled(False)
            if row.is_checked() == answer.correct:
                if answer.correct:
                    row.set_state(True)
            else:
                row.set_state(False)
                all_correct = False
                wrong_this_question += 1

        self.answered_count += 1
        self.wrong_count += wrong_this_question
        if all_correct:
            self.correct_count += 1
        self._update_score_label()

        if self.current.description:
            self.description_label.setText(self.current.description)

        if not self.result_shown and self.answered_count >= QUESTION_LIMIT:
            self.result_shown = True
            if self.wrong_count >= WRONG_THRESHOLD:
                self._show_gif(GIF_BAD_PATH, "Zu viele Fehler!")
            else:
                self._show_gif(GIF_GOOD_PATH, "Gut gemacht!")
        elif (
            not self.result_shown
            and self.wrong_count >= WRONG_THRESHOLD
        ):
            self.result_shown = True
            self._show_gif(GIF_BAD_PATH, "Zu viele Fehler!")

    def _show_gif(self, gif_path: Path, title: str) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout(dialog)
        label = QLabel()
        movie = QMovie(str(gif_path))
        label.setMovie(movie)
        layout.addWidget(label)
        movie.start()
        dialog.exec()


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))

    questions = load_questions()
    if not questions:
        QMessageBox.critical(
            None,
            "Keine Fragen gefunden",
            "Im Fragenpool wurden keine Fragen gefunden.",
        )
        return

    window = QuizWindow(questions)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
