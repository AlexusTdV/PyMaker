# PyMaker — GUI для быстрого создания `.py` файлов

[![Build](https://img.shields.io/github/actions/workflow/status/alexustdv/pymaker/build.yml?label=build)](#)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](#)
[![PyQt6](https://img.shields.io/badge/PyQt-6-41b883)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Простая утилита на **PyQt6** для быстрого создания Python‑файлов в выбранной папке.

-   Встроенное окно кода
-   Выбор базовой папки и создание внутренней подпапки
-   Имя файла по умолчанию `main.py`
-   Опции: открыть файл и/или папку после создания

## Установка и запуск

```bash
pip install -r requirements.txt
python main.py
```

## Сборка исполняемых файлов (CI)

Готовые сборки публикуются в артефактах GitHub Actions после каждого push.
Локально можно собрать так:

```bash
pyinstaller -F -w main.py --icon=icon.ico --add-data "icon.ico;."
```

## Вклад

Pull Request'ы приветствуются! См. [CONTRIBUTING.md](CONTRIBUTING.md).

---

### English

Simple **PyQt6** utility to quickly create Python `.py` files in a chosen folder, with optional subfolder creation and auto‑open options.
