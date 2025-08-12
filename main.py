import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton,
    QMessageBox, QLabel, QFileDialog, QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import QStandardPaths
from PyQt6.QtGui import QIcon


class CodeSaverApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyMaker — Создание .py файла")
        self.setMinimumWidth(560)

        # === ИКОНКА ОКНА ===
        app_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(app_dir, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout()

        # Поле для кода
        layout.addWidget(QLabel("Введите код:"))
        self.code_input = QTextEdit()
        self.code_input.setPlaceholderText("# Ваш код здесь")
        layout.addWidget(self.code_input)

        # Базовая папка
        layout.addWidget(QLabel("Базовая папка (куда будет создана внутренняя папка):"))
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Выберите базовую папку...")
        # Автоподстановка Рабочего стола
        desktop_paths = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)
        if desktop_paths:
            self.folder_input.setText(desktop_paths[0])
        select_folder_btn = QPushButton("📂")
        select_folder_btn.setFixedWidth(40)
        select_folder_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(select_folder_btn)
        layout.addLayout(folder_layout)

        # Имя внутренней папки
        layout.addWidget(QLabel("Имя внутренней папки (будет создана внутри выбранной):"))
        self.subfolder_input = QLineEdit()
        self.subfolder_input.setPlaceholderText("например, my_project (необязательно)")
        layout.addWidget(self.subfolder_input)

        # Имя файла
        layout.addWidget(QLabel("Название файла:"))
        self.file_input = QLineEdit("main.py")
        layout.addWidget(self.file_input)

        # Галочки
        self.open_after_save = QCheckBox("Открыть файл после создания")
        self.open_folder_after_save = QCheckBox("Открыть папку после создания")
        layout.addWidget(self.open_after_save)
        layout.addWidget(self.open_folder_after_save)

        # Кнопка сохранить
        save_button = QPushButton("Создать файл")
        save_button.clicked.connect(self.save_file)
        layout.addWidget(save_button)

        self.setLayout(layout)

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
            QMessageBox.warning(self, "Ошибка", "Выберите базовую папку для сохранения.")
            return
        if not file_name:
            QMessageBox.warning(self, "Ошибка", "Введите название файла.")
            return
        if not file_name.endswith(".py"):
            file_name += ".py"

        # Итоговая папка: base_folder[/subfolder]
        target_folder = os.path.join(base_folder, subfolder) if subfolder else base_folder

        try:
            os.makedirs(target_folder, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать папку:\n{e}")
            return

        file_path = os.path.join(target_folder, file_name)

        # Записываем файл
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_text)

            QMessageBox.information(
                self, "Готово",
                f"Папка:\n{target_folder}\n\nФайл создан:\n{file_path}"
            )

            # Действия после создания
            if self.open_after_save.isChecked():
                self.open_path(file_path)
            if self.open_folder_after_save.isChecked():
                self.open_path(target_folder)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")

    def open_path(self, path):
        """Открывает файл или папку в системе."""
        try:
            if os.name == "nt":  # Windows
                os.startfile(path)
            elif sys.platform == "darwin":  # macOS
                subprocess.call(["open", path])
            else:  # Linux
                subprocess.call(["xdg-open", path])
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть:\n{path}\n\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Иконка для панели задач/дока
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(app_dir, "icon.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
    except Exception:
        pass

    window = CodeSaverApp()
    window.show()
    sys.exit(app.exec())
