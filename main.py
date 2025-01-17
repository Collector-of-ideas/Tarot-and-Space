import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pandas as pd
import random
import requests
from urllib.request import urlopen
from datetime import datetime

'''Эта программа изначально должна была работать только с Таро, но мы подумали - почему бы не объединить астрологию с астрономией?
И добавили в неё фотографии, сделанные NASA. Теперь вы можете рассчитать арканы по своей дате рождения и посмотреть, какое фото
сделали в космосе в тот день, когда вы родились, а также получить рандомизированное предсказание на день. Пользуйтесь с умом :)'''

# создание приложения как класса для упрощения дальнейшей работы

class TarotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Таро и космос")

        # установка размера окна
        self.X = root.winfo_screenwidth()
        self.Y = root.winfo_screenheight()
        self.root.geometry(f"{self.X}x{self.Y}")
        self.root.resizable(True, True)

        # чтение данных из Excel-файла, там представлены описания арканов
        self.excel_file = "arcana_descriptions.xlsx"
        self.df = pd.read_excel(self.excel_file)

        # создание виджетов
        self.create_widgets()

    def create_widgets(self):
        # верхняя панель для выбора даты, ввод с клавиатуры может привести к ошибкам, поэтому все значения выводим списками
        # по умолчанию стоит 01.01.2000
        self.date_frame = tk.Frame(self.root)
        self.date_frame.pack(pady=10)

        # выбор дня из выпадающего списка
        self.day_label = tk.Label(self.date_frame, text="День:", font=("Arial", 14))
        self.day_label.grid(row=0, column=0)
        self.day_combobox = ttk.Combobox(self.date_frame, values=[str(i).zfill(2) for i in range(1, 32)], font=("Arial", 14))
        self.day_combobox.set("01")
        self.day_combobox.grid(row=0, column=1)

        # выбор месяца из выпадающего списка
        self.month_label = tk.Label(self.date_frame, text="Месяц:", font=("Arial", 14))
        self.month_label.grid(row=0, column=2)
        self.month_combobox = ttk.Combobox(self.date_frame, values=[str(i).zfill(2) for i in range(1, 13)], font=("Arial", 14))
        self.month_combobox.set("01")
        self.month_combobox.grid(row=0, column=3)

        # выбор года из выпадающего списка
        self.year_label = tk.Label(self.date_frame, text="Год:", font=("Arial", 14))
        self.year_label.grid(row=0, column=4)
        self.year_combobox = ttk.Combobox(self.date_frame, values=[str(i) for i in range(1900, 2026)], font=("Arial", 14))
        self.year_combobox.set("2000")
        self.year_combobox.grid(row=0, column=5)

        # отрисовка трёх кнопок
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=10)

        self.calculate_button = tk.Button(self.buttons_frame, text="Рассчитать арканы", command=self.calculate_arcana, font=("Arial", 14))
        self.calculate_button.pack(side="left", padx=10)

        self.daily_prediction_button = tk.Button(self.buttons_frame, text="Рассчитать предсказание на день", command=self.calculate_daily_prediction, font=("Arial", 14))
        self.daily_prediction_button.pack(side="left", padx=10)

        self.nasa_fetch_button = tk.Button(self.buttons_frame, text="Загрузить изображение NASA", command=self.get_apod_by_date, font=("Arial", 14))
        self.nasa_fetch_button.pack(side="left", padx=10)

        # создание фрейма для арканов по дате рождения (внутри него будут ещё 2)
        self.arcana_frame = tk.Frame(self.root)
        self.arcana_frame.pack(side="left", padx=20, fill=tk.Y)

        # создание фреймов для отображения арканов внутри общего
        self.arcana1_frame = self.create_arcana_frame(self.arcana_frame)
        self.arcana2_frame = self.create_arcana_frame(self.arcana_frame)

        # основной фрейм для предсказания на день и фотографии NASA
        self.results_frame = tk.Frame(self.root)
        self.results_frame.pack(side="right", padx=30, fill=tk.Y)

        # фрейм для предсказания на день, располагаем карту, название и описание сверху вниз
        self.daily_arcana_frame = tk.Frame(self.results_frame)
        self.daily_arcana_frame.pack(side="left", pady=10)

        self.daily_arcana_image_label = tk.Label(self.daily_arcana_frame)
        self.daily_arcana_image_label.pack(side="top")

        self.daily_arcana_name_label = tk.Label(self.daily_arcana_frame, text="", font=("Arial", 14, "bold"))
        self.daily_arcana_name_label.pack(side="top")

        # устанавливаем wraplength=250 для регулировки ширины получившегося текста с описанием
        self.daily_arcana_description_label = tk.Label(self.daily_arcana_frame, text="", wraplength=250, font=("Arial", 14))
        self.daily_arcana_description_label.pack(side="top")

        # создание фрейма для расположения предсказания на день и фотографии NASA
        self.lower_frame = tk.Frame(self.results_frame)
        self.lower_frame.pack(side="left", pady=10)

        # фрейм для фото NASA
        self.nasa_frame = tk.Frame(self.lower_frame)
        self.nasa_frame.pack(side="right")

        self.title_label = tk.Label(self.nasa_frame, text="", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)

        # пишем пользователю, в какой промежуток должна входить дата, если введёт другую, программа выдаст ошибку
        self.explanation_text = tk.Text(self.nasa_frame, height=5, width=60, font=("Arial", 14))
        self.explanation_text.pack(pady=10)
        self.explanation_text.insert(tk.END, f"Для получения изображения от NASA дата должна принадлежать следующему временному промежутку: от 1995-06-16 до {datetime.now().strftime("%Y-%m-%d")}")

        # для отображения изображения
        self.nasa_image_label = tk.Label(self.nasa_frame)
        self.nasa_image_label.pack(pady=10)

        # установка расположения арканов
        self.arcana1_frame[3].pack(side="left", padx=10)
        self.arcana2_frame[3].pack(side="right", padx=10)

    # функция для создания фреймов для арканов (при выводе двух арканов по дате рождения)
    def create_arcana_frame(self, parent):
        frame = tk.Frame(parent)

        arcana_image_label = tk.Label(frame)
        arcana_image_label.pack(side="top")

        arcana_name_label = tk.Label(frame, text="", font=("Arial", 14, "bold"))
        arcana_name_label.pack(side="top")

        arcana_description_label = tk.Label(frame, text="", wraplength=250, font=("Arial", 14))
        arcana_description_label.pack(side="top")
        
        # устанавливаем расстояние между рамками
        frame.pack(side="top", padx=10)  
        return (arcana_image_label, arcana_name_label, arcana_description_label, frame)
    
    # очищаем результаты арканов
    def clear_results(self):
        for arcana in [self.arcana1_frame, self.arcana2_frame]:
            arcana[0].config(image="")
            arcana[1].config(text="")
            arcana[2].config(text="")

    # функция дла расчёта двух арканов по дате рождения
    def calculate_arcana(self):
        self.clear_results()
        day = int(self.day_combobox.get())
        month = int(self.month_combobox.get())
        year = int(self.year_combobox.get())
        
        # первый аркан рассчитывается как сумма цифр даты рождения, второй - число даты рождения
        sum_of_digits = sum(int(digit) for digit in str(day)) + sum(int(digit) for digit in str(month)) + sum(int(digit) for digit in str(year))
        arcana_number1 = sum_of_digits % 22
        arcana_number2 = day % 22
        # используем остаток от деления на 22, т.к. старших арканов таро всего 22, они нумеруются от 0 до 21

        # загрузка изображений арканов
        self.update_arcana_image(arcana_number1, self.arcana1_frame)
        self.update_arcana_image(arcana_number2, self.arcana2_frame)

    # функция для обновления изображения арканов, в папке заранее лежат пронумерованные соответствующим образом ассеты
    # пользуемся библиотекой PIL
    def update_arcana_image(self, arcana_number, arcana_frame):
        image = Image.open(f"arcana_images/{arcana_number}.png")
        image = image.resize((150, 267))
        imageTk = ImageTk.PhotoImage(image)

        arcana_frame[0].config(image=imageTk)
        arcana_frame[0].image = imageTk  # сохраняем ссылку на изображение

        arcana_name = self.df.iloc[arcana_number, 0]
        arcana_description = self.df.iloc[arcana_number, 1]

        arcana_frame[1].config(text=arcana_name)
        arcana_frame[2].config(text=arcana_description)

    # рандомизированный расчёт предсказания на день по аркану Таро
    def calculate_daily_prediction(self):
        self.clear_daily_prediction_results()
        arcana_number = random.randint(0, 21)
        self.update_arcana_image(arcana_number, (self.daily_arcana_image_label, self.daily_arcana_name_label, self.daily_arcana_description_label))

    def clear_daily_prediction_results(self):
        self.daily_arcana_image_label.config(image="")
        self.daily_arcana_name_label.config(text="")
        self.daily_arcana_description_label.config(text="")
    
    # через открытый API NASA получаем фотографию, сделанную в определённую дату
    def fetch_apod(self, date):
        api_key = "pvmwhWhvxMy9AC3LNyj6JjcLaZOA8zcENteIIqyo"
        url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}&date={date}"

        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка: {response.status_code} - {response.text}")
            return None

    def get_apod_by_date(self):
        date_input = f"{self.year_combobox.get()}-{self.month_combobox.get()}-{self.day_combobox.get()}"
        try:
            response_data = self.fetch_apod(date_input)
            if response_data:
                title = response_data.get("title")
                explanation = response_data.get("explanation")
                image_url = response_data.get("url")

                self.title_label.config(text=title)
                self.explanation_text.delete(1.0, tk.END)
                self.explanation_text.insert(tk.END, explanation)

                self.display_nasa_image(image_url)
            else:
                messagebox.showerror("Ошибка", "Не удалось получить данные изображения.")
        except ValueError:
            messagebox.showerror("Ошибка", "Не удалось получить данные изображения.")

    def display_nasa_image(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            pil_image = Image.open(urlopen(url))
            img = ImageTk.PhotoImage(pil_image)

            self.nasa_image_label.configure(image=img)
            self.nasa_image_label.image = img
        else:
            messagebox.showerror("Ошибка", "Не удалось загрузить изображение.")

# создание основного окна приложения
root = tk.Tk()

# создание экземпляра приложения (используем созданный ранее класс TarotApp)
app = TarotApp(root)

# запуск главного цикла приложения
root.mainloop()