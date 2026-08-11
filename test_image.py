"""Test script to display a single question with an image for visual verification."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from questions import load_questions


class SingleQuestionWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Image Test")
        self.resize(750, 700)

        questions = load_questions()
        self.image_questions = [q for q in questions if q.image is not None]
        if not self.image_questions:
            QLabel("No questions with images found.")
            return

        self.index = 0
        self._build_ui()
        self._show_question()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        self.category_label = QLabel()
        self.category_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        root.addWidget(self.category_label)

        self.question_label = QLabel()
        self.question_label.setFont(QFont("Segoe UI", 15))
        self.question_label.setWordWrap(True)
        root.addWidget(self.question_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.image_label)

        self.path_label = QLabel()
        self.path_label.setFont(QFont("Segoe UI", 9))
        self.path_label.setStyleSheet("color: #9aa0a6;")
        root.addWidget(self.path_label)

        self.answers_layout = QVBoxLayout()
        self.answers_layout.setSpacing(8)
        root.addLayout(self.answers_layout)

        root.addStretch()

        from PySide6.QtWidgets import QPushButton

        self.next_button = QPushButton("Next image question")
        self.next_button.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.next_button.setMinimumHeight(50)
        self.next_button.clicked.connect(self._next)
        root.addWidget(self.next_button)

    def _show_question(self) -> None:
        q = self.image_questions[self.index]
        self.category_label.setText(q.category)
        self.question_label.setText(q.text)

        if q.image is not None and q.image.is_file():
            pixmap = QPixmap(str(q.image))
            if not pixmap.isNull():
                scaled = pixmap.scaledToWidth(600, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(scaled)
                self.path_label.setText(f"Image: {q.image}")
            else:
                self.image_label.setText("Failed to load image")
                self.path_label.setText(f"Image: {q.image}")
        else:
            self.image_label.setText("Image file not found")
            self.path_label.setText(f"Expected: {q.image}")

        for i in range(self.answers_layout.count()):
            item = self.answers_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for answer in q.answers:
            row = QFrame()
            row.setStyleSheet(
                "QFrame { background-color: #2e7d32; border-radius: 6px; }"
                if answer.correct
                else "QFrame { background-color: transparent; border-radius: 6px; }"
            )
            layout = QHBoxLayout(row)
            layout.setContentsMargins(10, 6, 10, 6)
            cb = QCheckBox()
            cb.setChecked(answer.correct)
            cb.setEnabled(False)
            layout.addWidget(cb)
            label = QLabel(answer.text)
            label.setWordWrap(True)
            label.setFont(QFont("Segoe UI", 12))
            layout.addWidget(label, stretch=1)
            self.answers_layout.addWidget(row)

    def _next(self) -> None:
        self.index = (self.index + 1) % len(self.image_questions)
        self._show_question()


def main() -> None:
    app = QApplication(sys.argv)
    window = SingleQuestionWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
