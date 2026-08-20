"""Test script to display a single question with a long description for visual verification
of the scrollable description area."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from questions import load_questions


class SingleQuestionWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Description Scroll Test")
        self.resize(750, 700)

        questions = load_questions()
        self.description_questions = sorted(
            (q for q in questions if q.description),
            key=lambda q: len(q.description or ""),
            reverse=True,
        )
        if not self.description_questions:
            QLabel("No questions with a description found.")
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

        self.answers_layout = QVBoxLayout()
        self.answers_layout.setSpacing(8)
        root.addLayout(self.answers_layout)

        self.length_label = QLabel()
        self.length_label.setFont(QFont("Segoe UI", 9))
        self.length_label.setStyleSheet("color: #9aa0a6;")
        root.addWidget(self.length_label)

        # Reuse the same description widget setup as main.py (QScrollArea around a QLabel).
        self.description_label = QLabel()
        self.description_label.setFont(QFont("Segoe UI", 10))
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #9aa0a6;")
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.description_scroll = QScrollArea()
        self.description_scroll.setWidget(self.description_label)
        self.description_scroll.setWidgetResizable(True)
        self.description_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.description_scroll.setMaximumHeight(150)
        self.description_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        root.addWidget(self.description_scroll)

        root.addStretch()

        self.next_button = QPushButton("Next description question")
        self.next_button.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.next_button.setMinimumHeight(50)
        self.next_button.clicked.connect(self._next)
        root.addWidget(self.next_button)

    def _show_question(self) -> None:
        q = self.description_questions[self.index]
        self.category_label.setText(q.category)
        self.question_label.setText(q.text)
        self.description_label.setText(q.description or "")
        self.length_label.setText(f"Description length: {len(q.description or '')} characters")

        if q.image is not None and q.image.is_file():
            pixmap = QPixmap(str(q.image))
            if not pixmap.isNull():
                scaled = pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(scaled)
            else:
                self.image_label.setText("Failed to load image")
        else:
            self.image_label.setText("Image file not found")

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
            label = QLabel(answer.text)
            label.setWordWrap(True)
            label.setFont(QFont("Segoe UI", 12))
            layout.addWidget(label, stretch=1)
            self.answers_layout.addWidget(row)

    def _next(self) -> None:
        self.index = (self.index + 1) % len(self.description_questions)
        self._show_question()


def main() -> None:
    app = QApplication(sys.argv)
    window = SingleQuestionWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
