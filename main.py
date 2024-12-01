import sys
# Введите в терминале pip install pyqt5
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QWidget, QLineEdit, QLabel, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
import sqlite3
import os
import webbrowser


class BookstoreApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Книжный магазин")
        self.setGeometry(100, 100, 900, 600)

        # Подключение к базе данных
        self.conn = sqlite3.connect("bookstore.db")
        self.create_table()

        # Основной виджет и макет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        # Поля для добавления книг
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Название книги")
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Автор")
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Год книги")

        self.add_button = QPushButton("Добавить книгу")
        self.add_button.clicked.connect(self.add_book)

        self.layout.addWidget(QLabel("Добавить книгу"))
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(self.author_input)
        self.layout.addWidget(self.year_input)
        self.layout.addWidget(self.add_button)

        # Кнопка для загрузки файла
        self.upload_button = QPushButton("Загрузить файл (PDF/DOCX)")
        self.upload_button.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_button)

        # Таблица для отображения книг
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Автор", "Год книги", "Файл"])
        self.layout.addWidget(self.table)

        # Кнопки управления
        self.refresh_button = QPushButton("Обновить список")
        self.refresh_button.clicked.connect(self.load_books)
        self.layout.addWidget(self.refresh_button)

        self.delete_button = QPushButton("Удалить выбранную книгу")
        self.delete_button.clicked.connect(self.delete_book)
        self.layout.addWidget(self.delete_button)

        self.central_widget.setLayout(self.layout)

        # Загрузка данных при старте
        self.load_books()

        self.file_path = None  # Путь к загруженному файлу

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            year_book INTEGER,
            file_path TEXT
        )
        """)
        self.conn.commit()

    def add_book(self):
        title = self.title_input.text()
        author = self.author_input.text()
        year_book = self.year_input.text()

        if not title or not author or not year_book:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            year_book = int(year_book)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Год должен быть числом!")
            return

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, author, year_book, file_path) VALUES (?, ?, ?, ?)",
            (title, author, year_book, self.file_path)
        )
        self.conn.commit()

        QMessageBox.information(self, "Успех", "Книга добавлена!")
        self.file_path = None  # Сброс пути файла после добавления книги
        self.load_books()

    def load_books(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, author, year_book, file_path FROM books")
        books = cursor.fetchall()

        self.table.setRowCount(len(books))
        for row_idx, (book_id, title, author, year_book, file_path) in enumerate(books):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(book_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(title))
            self.table.setItem(row_idx, 2, QTableWidgetItem(author))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(year_book)))

            # Добавляем кнопку для открытия файла
            open_button = QPushButton("Открыть файл")
            open_button.clicked.connect(lambda _, path=file_path: self.open_file(path))
            self.table.setCellWidget(row_idx, 4, open_button)

    def delete_book(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для удаления!")
            return

        book_id = self.table.item(selected_row, 0).text()
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self.conn.commit()

        QMessageBox.information(self, "Успех", "Книга удалена!")
        self.load_books()

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл", "", "PDF Files (*.pdf);;Word Documents (*.docx)"
        )
        if not file_path:
            return

        if not (file_path.endswith(".pdf") or file_path.endswith(".docx")):
            QMessageBox.warning(self, "Ошибка", "Вы можете загрузить только PDF или DOCX файлы!")
            return

        self.file_path = file_path
        QMessageBox.information(self, "Успех", f"Файл загружен: {os.path.basename(file_path)}")

    def open_file(self, file_path):
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Ошибка", "Файл не найден!")
            return

        try:
            webbrowser.open(file_path)  # Открывает файл с помощью системного приложения
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookstoreApp()
    window.show()
    sys.exit(app.exec_())
