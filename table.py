import tkinter as tk
from tkinter import ttk
import sqlite3


def delete_row():
    # Получаем выбранный элемент в виде дерева (TreeView)
    selected_item = treeview.focus()
    # Проверяем, что элемент выбран
    if selected_item:
        # Получаем значения выбранного элемента
        values = treeview.item(selected_item, 'values')
        # Извлекаем идентификатор сотрудника для удаления
        id_to_delete = values[0]
        # Удаляем сотрудника из базы данных по его идентификатору
        cursor.execute("DELETE FROM Employees WHERE id=?", (id_to_delete,))
        # Фиксируем изменения в базе данных
        conn.commit()
        # Удаляем выбранный элемент из TreeView
        treeview.delete(selected_item)


def search():
    # Получаем ключевое слово для поиска из поля ввода
    search_keyword = search_entry.get()
    # Проверяем, что ключевое слово для поиска не пустое
    if search_keyword:
        # Очищаем TreeView перед добавлением новых данных
        treeview.delete(*treeview.get_children())
        # Выполняем запрос на выборку сотрудников из базы данных, соответствующих ключевому слову
        cursor.execute(
            "SELECT id, first_name, last_name, position, created_at FROM Employees WHERE first_name LIKE ? OR last_name LIKE ? OR position LIKE ?",
            ('%' + search_keyword + '%', '%' + search_keyword + '%', '%' + search_keyword + '%'))
        # Получаем строки, соответствующие запросу
        rows = cursor.fetchall()
        # Добавляем каждую строку в TreeView для отображения результатов поиска
        for row in rows:
            treeview.insert('', 'end', values=row)


def reset_search():
    # Очищаем поле ввода для поиска
    search_entry.delete(0, 'end')
    # Очищаем TreeView
    treeview.delete(*treeview.get_children())
    # Получаем все записи о сотрудниках из базы данных
    cursor.execute("SELECT id, first_name, last_name, position, created_at FROM Employees")
    # Получаем строки, соответствующие запросу
    rows = cursor.fetchall()
    # Добавляем каждую строку в TreeView для отображения всех записей
    for row in rows:
        treeview.insert('', 'end', values=row)


# Устанавливаем соединение с базой данных SQLite
conn = sqlite3.connect('database.db')
# Создаем курсор для выполнения операций с базой данных
cursor = conn.cursor()

root = tk.Tk()
root.title("Таблица сотрудников")
root.geometry("1020x500")
root.resizable(False, False)
root.configure(background='#78defc')
search_entry = tk.Entry(root, width=25)
search_entry.place(x=10, y=12)
search_button = tk.Button(root, text="Поиск", command=search, width=10)
search_button.place(x=200, y=10)
reset_button = tk.Button(root, text="Сброс", command=reset_search, width=10)
reset_button.place(x=280, y=10)
delete_button = tk.Button(root, text="Удалить запись", command=delete_row)
delete_button.place(x=915, y=10)
treeview = ttk.Treeview(root, columns=('ID', 'First Name', 'Last Name', 'Position', 'Created At'),
                        show='headings', height=12)
treeview.heading('ID', text='ID')
treeview.heading('First Name', text='First Name')
treeview.heading('Last Name', text='Last Name')
treeview.heading('Position', text='Position')
treeview.heading('Created At', text='Created At')

# Выполняем запрос к базе данных для выборки всех записей о сотрудниках
cursor.execute("SELECT id, first_name, last_name, position, created_at FROM Employees")
# Получаем все строки (записи) из результата выполнения запроса
rows = cursor.fetchall()
# Для каждой строки в результатах выполненного запроса
for row in rows:
    # Добавляем новый элемент (строку) в TreeView (дерево)
    # 'end' указывает на то, что новый элемент добавляется в конец дерева
    # values=row добавляет значения из строки как значения элемента TreeView
    treeview.insert('', 'end', values=row)
treeview.place(x=10, y=40)
root.mainloop()

