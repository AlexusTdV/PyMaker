import sys
import os
import subprocess
from PyQt6.QtCore import Qt, QRect, QSize, QStandardPaths
from PyQt6.QtGui import (
    QIcon,
    QColor,
    QPainter,
    QFont,
    QTextFormat,
    QSyntaxHighlighter,
    QTextCharFormat,
)
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QLabel,
    QFileDialog,
    QHBoxLayout,
    QCheckBox,
    QPlainTextEdit,
    QSizePolicy,
    QTextEdit,
)


# ---------------------------
# Гуттер с номерами строк
# ---------------------------
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


# ---------------------------
# Редактор кода в стиле VS
# ---------------------------
class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Шрифт
        font = QFont("Consolas")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(11)
        self.setFont(font)

        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Гуттер
        self._lineNumberArea = LineNumberArea(self)

        # Сигналы
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance("9") * digits

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self._lineNumberArea.scroll(0, dy)
        else:
            self._lineNumberArea.update(
                0, rect.y(), self._lineNumberArea.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._lineNumberArea.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        )

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self._lineNumberArea)
        painter.fillRect(event.rect(), QColor(245, 245, 245))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor(120, 120, 120))
                painter.drawText(
                    0,
                    top,
                    self._lineNumberArea.width() - 4,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(232, 242, 254)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)


# ---------------------------
# Подсветка синтаксиса Python
# ---------------------------
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        def fmt(color, bold=False, italic=False):
            _fmt = QTextCharFormat()
            _fmt.setForeground(QColor(color))
            if bold:
                _fmt.setFontWeight(QFont.Weight.Bold)
            if italic:
                _fmt.setFontItalic(True)
            return _fmt

        self.rules = []
        import re

        keywords = (
            r"\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|"
            r"elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|"
            r"not|or|pass|raise|return|try|while|with|yield)\b"
        )
        builtins = (
            r"\b(abs|all|any|ascii|bin|bool|bytearray|bytes|callable|chr|classmethod|"
            r"compile|complex|dict|dir|divmod|enumerate|eval|exec|filter|float|format|"
            r"frozenset|getattr|globals|hasattr|hash|help|hex|id|input|int|isinstance|"
            r"issubclass|iter|len|list|locals|map|max|memoryview|min|next|object|oct|"
            r"open|ord|pow|print|property|range|repr|reversed|round|set|setattr|slice|"
            r"sorted|staticmethod|str|sum|super|tuple|type|vars|zip)\b"
        )

        self.rules.append((re.compile(keywords), fmt("#0000FF", bold=True)))
        self.rules.append((re.compile(builtins), fmt("#2B91AF")))
        self.rules.append((re.compile(r"#.*"), fmt("#008000", italic=True)))
        self.rules.append((re.compile(r"\b[0-9]+\b"), fmt("#098658")))
        self.rules.append((re.compile(r"(\"[^\"]*\"|'[^']*')"), fmt("#A31515")))

    def highlightBlock(self, text):
        for pattern, format in self.rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


# ---------------------------
# Главное приложение
# ---------------------------
class CodeSaverApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyMaker — Создание .py файла")
        self.setMinimumWidth(700)

        app_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(app_dir, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(self)

        # Редактор кода
        layout.addWidget(QLabel("Код (Python):"))
        self.code_input = CodeEditor()
        PythonHighlighter(self.code_input.document())
        layout.addWidget(self.code_input)

        # Базовая папка
        layout.addWidget(QLabel("Базовая папка:"))
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        desktop_paths = QStandardPaths.standardLocations(
            QStandardPaths.StandardLocation.DesktopLocation
        )
        if desktop_paths:
            self.folder_input.setText(desktop_paths[0])
        btn_pick = QPushButton("📂")
        btn_pick.setFixedWidth(40)
        btn_pick.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(btn_pick)
        layout.addLayout(folder_layout)

        # Имя внутренней папки
        layout.addWidget(QLabel("Имя внутренней папки (необязательно):"))
        self.subfolder_input = QLineEdit()
        layout.addWidget(self.subfolder_input)

        # Имя файла
        layout.addWidget(QLabel("Название файла:"))
        self.file_input = QLineEdit("main.py")
        layout.addWidget(self.file_input)

        # Опции
        self.open_after_save = QCheckBox("Открыть файл после создания")
        self.open_folder_after_save = QCheckBox("Открыть папку после создания")
        layout.addWidget(self.open_after_save)
        layout.addWidget(self.open_folder_after_save)

        # Кнопка
        btn_create = QPushButton("Создать файл")
        btn_create.clicked.connect(self.save_file)
        layout.addWidget(btn_create)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder:
            self.folder_input.setText(folder)

    def save_file(self):
        base_folder = self.folder_input.text().strip()
        subfolder = self.subfolder_input.text().strip()
        file_name = self.file_input.text().strip()
        code_text = self.code_input.toPlainText()

        if not base_folder:
            QMessageBox.warning(self, "Ошибка", "Выберите базовую папку.")
            return
        if not file_name:
            QMessageBox.warning(self, "Ошибка", "Введите название файла.")
            return
        if not file_name.endswith(".py"):
            file_name += ".py"

        target_folder = (
            os.path.join(base_folder, subfolder) if subfolder else base_folder
        )
        os.makedirs(target_folder, exist_ok=True)
        file_path = os.path.join(target_folder, file_name)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_text)
            QMessageBox.information(self, "Готово", f"Файл создан:\n{file_path}")
            if self.open_after_save.isChecked():
                self.open_path(file_path)
            if self.open_folder_after_save.isChecked():
                self.open_path(target_folder)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")

    def open_path(self, path):
        try:
            if os.name == "nt":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть:\n{path}\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(app_dir, "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    window = CodeSaverApp()
    window.show()
    sys.exit(app.exec())
