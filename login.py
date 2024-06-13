import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
import cv2
import telebot

token = '6817582327:AAGa0SOHs2vk_-ddzdzyufE72SrMrOv2F4M'
bot = telebot.TeleBot(token)
chat_id = '1034417507'


def TrackImages():
    # Создаем экземпляр распознавателя лиц методом LBPH (Local Binary Patterns Histograms)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    # Проверяем, существует ли файл "Trainner.yml", содержащий обученную модель распознавателя
    exists = os.path.isfile("TrainingImageLabel/Trainner.yml")
    # Если файл существует, загружаем обученную модель
    if exists:
        recognizer.read("TrainingImageLabel/Trainner.yml")
    else:
        # Если файл не найден, выводим сообщение об ошибке и прерываем выполнение функции
        messagebox.showerror(title='Не найдено Trainner.yml', message='Пожалуйста зарегистрируйте профиль')
        return
    # Устанавливаем соединение с базой данных SQLite
    conn = sqlite3.connect('database.db')
    # Создаем курсор для выполнения операций с базой данных
    cursor = conn.cursor()
    # Загружаем классификатор каскада Хаара для обнаружения лиц
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # Захватываем видеопоток с веб-камеры
    cam = cv2.VideoCapture(0)
    # Устанавливаем шрифт для отображения текста на изображении
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Глобальная переменная для хранения имени сотрудника
    global employee_name
    employee_name = None
    # Бесконечный цикл для обработки каждого кадра видеопотока
    while True:
        # Считываем кадр из видеопотока
        ret, img = cam.read()
        # Преобразуем изображение в оттенки серого
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Обнаруживаем лица на изображении с помощью каскада Хаара
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        # Обходим каждое обнаруженное лицо
        for (x, y, w, h) in faces:
            # Рисуем прямоугольник вокруг лица на изображении
            cv2.rectangle(img, (x, y), (x + w, y + h), (225, 0, 0), 2)
            # Предсказываем идентификатор лица и уверенность (доверие) предсказания
            serial, conf = recognizer.predict(gray[y:y + h, x:x + w])
            # Если уверенность предсказания меньше 50, пытаемся получить информацию о сотруднике из базы данных
            if conf < 50:
                cursor.execute("SELECT id, first_name, last_name, password FROM Employees WHERE id = ?", (serial,))
                employee_info = cursor.fetchone()
                # Если информация о сотруднике найдена, формируем строку посещаемости с именем сотрудника
                if employee_info:
                    employee_id, last_name, first_name, password = employee_info
                    attendance = [str(employee_id), '', last_name + ' ' + first_name]
                    employee_name = attendance[2]
                else:
                    # Если информация о сотруднике не найдена, помечаем его как "Неизвестный"
                    attendance = ['Unknown', '', 'Unknown']
            else:
                # Если уверенность предсказания выше 50, помечаем сотрудника как "Неизвестный"
                attendance = ['Unknown', '', 'Unknown']
            # Отображаем имя сотрудника на изображении
            cv2.putText(img, str(attendance[2]), (x, y + h), font, 1, (255, 255, 255), 2)
        # Отображаем изображение с нарисованными прямоугольниками и именами сотрудников
        cv2.imshow('Taking Attendance', img)
        # Если пользователь нажал клавишу 'q', выходим из цикла
        if cv2.waitKey(1) == ord('q'):
            break
    # Освобождаем ресурсы камеры
    cam.release()
    # Закрываем все окна OpenCV
    cv2.destroyAllWindows()


def check_credentials(login, password):
    # Устанавливаем соединение с базой данных SQLite
    conn = sqlite3.connect('database.db')
    # Создаем курсор для выполнения операций с базой данных
    cursor = conn.cursor()
    # Выполняем запрос на выборку записей из таблицы Employees с указанным логином и паролем
    cursor.execute("SELECT * FROM Employees WHERE first_name || ' ' || last_name = ? AND password = ?",
                   (login, password))
    # Получаем первую запись, соответствующую запросу
    row = cursor.fetchone()
    # Закрываем соединение с базой данных
    conn.close()
    # Проверяем, найдена ли запись
    return row is not None


def loginSystem():
    # Получаем введенные пользователем логин и пароль
    login = entry1.get()
    password = entry2.get()
    # Проверяем корректность введенных учетных данных и соответствие имени сотрудника лицу
    if check_credentials(login, password) and employee_name == login:
        # Выводим сообщение об успешной авторизации
        messagebox.showinfo("Успех", "Авторизация успешна!")
    else:
        # Если учетные данные неверны или лицо не распознано, выводим сообщение об ошибке
        messagebox.showerror("Ошибка", "Неверный логин или пароль или лицо не распознано")
        # Отправляем сообщение в Телеграм
        bot.send_message(chat_id, f"{login} ({employee_name}), не удачная попытка авторизации")


root = tk.Tk()
root.title("Login")
root.geometry("700x400")
root.resizable(False, False)
root.configure(background='#78defc')
label1 = tk.Label(root, text="Login:", font=("Helvetica", 14), background='#78defc')
label1.place(x=150, y=100)
entry1 = tk.Entry(root)
entry1.place(x=230, y=100, height=25, width=300)
label2 = tk.Label(root, text="Пароль:", font=("Helvetica", 14), background='#78defc')
label2.place(x=150, y=140)
entry2 = tk.Entry(root, show="*")
entry2.place(x=230, y=140, height=25, width=300)
button1 = tk.Button(root, text="Распознание", width=15, command=TrackImages)
button1.place(x=300, y=180)
button2 = tk.Button(root, text="Вход", width=15, command=loginSystem)
button2.place(x=300, y=220)

root.mainloop()
