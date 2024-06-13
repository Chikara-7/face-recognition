import os
import subprocess
from tkinter import *
from tkinter import messagebox
import cv2
import sqlite3
import numpy as np
from PIL import Image


# Функция для получения нового id
def getID():
    conn = sqlite3.connect('database.db')  # Cоединение с бд
    cursor = conn.cursor()  # Создание курсор для операций с бд
    # SQL-запрос, выбирает максимальное значение столбца "id" из таблицы
    cursor.execute("SELECT MAX(id) FROM Employees")
    result = cursor.fetchone()  # Результат запроса
    conn.close()  # Закрытие соединения с бд
    if result[0] is None:  # Если результат пустой
        return 1  # Возвращает 1, id = 1
    else:
        return result[0] + 1  # id + 1


def TakeImages():
    # Устанавливаем соединение с базой данных SQLite, используя файл 'database.db'
    conn = sqlite3.connect('database.db')
    # Создаем курсор для выполнения операций с базой данных
    cursor = conn.cursor()
    # Инициализируем объект для захвата видео с камеры (webcam)
    cam = cv2.VideoCapture(0)
    # Загружаем классификатор каскада Хаара для обнаружения лиц
    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # Инициализируем переменную для хранения количества сделанных снимков
    sampleNum = 0
    # Получаем фамилию сотрудника из графического интерфейса (предполагается, что это текстовое поле)
    last_name = (TxtForLbl1.get())
    # Получаем имя сотрудника из графического интерфейса
    first_name = (TxtForLbl2.get())
    # Получаем должность сотрудника из графического интерфейса
    position = (TxtForLbl3.get())
    # Получаем новый уникальный идентификатор с помощью функции getID()
    id = getID()
    # Начинаем бесконечный цикл для захвата изображений с веб-камеры и их обработки
    while True:
        # Захватываем кадр с веб-камеры
        ret, img = cam.read()
        # Преобразуем изображение в оттенки серого
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Обнаруживаем лица на изображении с помощью каскада Хаара
        faces = detector.detectMultiScale(gray, 1.3, 5)
        # Обходим каждое обнаруженное лицо
        for (x, y, w, h) in faces:
            # Отрисовываем прямоугольник вокруг лица
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # Увеличиваем счетчик сделанных снимков
            sampleNum += 1
            # Сохраняем изображение лица в папку "TrainingImage"
            cv2.imwrite("TrainingImage/" + str(id) + "." + first_name + "." + last_name + "." + str(sampleNum) + ".jpg",
                        gray[y:y + h, x:x + w])
            # Отображаем изображение с прямоугольником в окне с названием 'Taking photo'
            cv2.imshow('Taking photo', img)
        # Если нажата клавиша 'q' или количество сделанных снимков больше 100, завершаем цикл
        if cv2.waitKey(100) & 0xFF == ord('q') or sampleNum > 100:
            break
    # Освобождаем ресурсы камеры
    cam.release()
    # Закрываем все окна OpenCV
    cv2.destroyAllWindows()
    # Пытаемся выполнить вставку информации о сотруднике в базу данных
    try:
        cursor.execute("INSERT INTO Employees (first_name, last_name, position) VALUES (?, ?, ?)",
                       (first_name, last_name, position))
        # Фиксируем изменения в базе данных
        conn.commit()
        # Отображаем информационное окно с сообщением об успешной операции
        result = "Снимки сделаны для: " + first_name
        messagebox.showinfo("Success", result)
    # Обрабатываем исключение, если произошла ошибка при выполнении SQL-запроса
    except sqlite3.Error as e:
        # Формируем сообщение об ошибке
        result = "Error: " + str(e)
        # Отображаем окно с сообщением об ошибке
        messagebox.showerror("Error", result)
    # В блоке finally закрываем соединение с базой данных независимо от того, произошла ошибка или нет
    finally:
        conn.close()


def getImagesAndLabels(path):
    # Получаем список путей к изображениям в указанной папке
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    # Инициализируем списки для хранения лиц (изображений) и их соответствующих идентификаторов
    faces = []
    IDs = []
    # Обходим каждый путь к изображению
    for imagePath in imagePaths:
        # Открываем изображение и конвертируем его в оттенки серого
        pilImage = Image.open(imagePath).convert('L')
        # Преобразуем изображение в массив numpy
        imageNp = np.array(pilImage, 'uint8')
        # Извлекаем идентификатор из имени файла изображения
        ID = int(os.path.split(imagePath)[-1].split(".")[0])
        # Добавляем лицо и его идентификатор в соответствующие списки
        faces.append(imageNp)
        IDs.append(ID)
    # Возвращаем списки лиц и их идентификаторов
    return faces, IDs


def TrainImages():
    # Создаем экземпляр LBPHFaceRecognizer для обучения
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    # Получаем лица (изображения) и их соответствующие идентификаторы из папки "TrainingImage"
    faces, IDs = getImagesAndLabels("TrainingImage")
    # Обучаем распознаватель лиц на полученных лицах и их идентификаторах
    recognizer.train(faces, np.array(IDs))
    # Сохраняем обученную модель распознавателя в файл "Trainner.yml" в папке "TrainingImageLabel"
    recognizer.save("TrainingImageLabel/Trainner.yml")
    # Формируем сообщение об успешном сохранении профиля
    result = "Профиль успешно сохранен"
    # Отображаем информационное сообщение пользователю
    messagebox.showinfo(message=result)


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
                cursor.execute("SELECT id, first_name, last_name FROM Employees WHERE id = ?", (serial,))
                employee_info = cursor.fetchone()
                # Если информация о сотруднике найдена, формируем строку посещаемости с именем сотрудника
                if employee_info:
                    employee_id, last_name, first_name = employee_info
                    attendance = [str(employee_id), '', last_name + ' ' + first_name]
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


root = Tk()
root.title("Face Recognition")
root.geometry("700x400")
root.resizable(False, False)

frame1 = Frame(root, width=350, height=400)
frame1.grid(row=0, column=0)
frame1.configure(bg="#37acf2")
trackImg = Button(frame1, text="Раcпознание", width=20, command=TrackImages)
trackImg.place(x=100, y=110)
listEmp = Button(frame1, text="Список", width=20, command=lambda: subprocess.run(["python", "table.py"]))
listEmp.place(x=100, y=160)

frame2 = Frame(root, width=350, height=400)
frame2.grid(row=0, column=1)
frame2.configure(bg="#78defc")
lbl1 = Label(frame2, text='Фамилия', background="#78defc", font=("Helvetica", 14))
lbl1.place(x=40, y=45)
TxtForLbl1 = Entry(frame2)
TxtForLbl1.place(x=150, y=50, width=170)
lbl2 = Label(frame2, text='Имя', background="#78defc", font=("Helvetica", 14))
lbl2.place(x=40, y=75)
TxtForLbl2 = Entry(frame2)
TxtForLbl2.place(x=150, y=80, width=170)
lbl3 = Label(frame2, text='Должность', background="#78defc", font=("Helvetica", 14))
lbl3.place(x=40, y=105)
TxtForLbl3 = Entry(frame2)
TxtForLbl3.place(x=150, y=110, width=170)
message = Label(frame2, text="Сделать фото >> Сохранить профиль", background="#78defc",
                font=("Helvetica", 11, "italic"))
message.place(x=42, y=142)
takeImg = Button(frame2, text="Сделать фото", width=20, command=TakeImages)
takeImg.place(x=100, y=175)
trainImg = Button(frame2, text="Сохранить профиль", width=20, command=TrainImages)
trainImg.place(x=100, y=215)

root.mainloop()
