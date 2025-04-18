from re import match
from unittest import case

import requests
from pprint import pprint
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import Frame, Label
import os
import json


# Создаем класс для работы с API ВКонтакте
class VK:
    def __init__(self, access_token, version='5.199'):
        self.params = {'access_token': access_token, 'v': version}
        self.base_url = 'https://api.vk.com/method/'

    # Функция запроса информации о профиле пользователя
    def users_info(self, user_id):
        url = f'{self.base_url}users.get'
        params = {'user_ids': user_id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    # Функция запроса информации о фотографиях в профиле пользователя
    def get_photos(self, user_id, count = 5):
        url = f'{self.base_url}photos.get'
        params = {'owner_id': user_id,'count': count,'album_id': program.album_combobox.get(),'extended': 1}
        params.update(self.params)
        response = requests.get(url, params=params)
        return response.json()

    # Функция запроса статуса профиля (не используется в данном приложении)
    def get_status(self, user_id):
        url = f'{self.base_url}status.get'
        params = {'owner_id': user_id}
        params.update(self.params)
        response = requests.get(url, params=params)
        return response.json()

# Создаем класс диалоговых сообщений
class MyDialog():
    def __init__(self, title_dialog, header_request):
        self.title_dialog = title_dialog
        self.header_request = header_request

    # Функция диалогового сообщения с полем ввода (не используется в данном приложении)
    def get_text(self):
        return simpledialog.askstring(title=self.title_dialog, prompt=self.header_request)

    # Функция диалогового сообщения с информацией
    def show_text(self):
        return messagebox.showinfo(self.title_dialog,self.header_request)

# Создаем класс графической оболочки приложения
class Counter_program():
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("FOTO_from_VK_to_YD")

        self.vk_frame = ttk.LabelFrame(self.window)
        self.token_label = ttk.Label(self.vk_frame)
        self.token_entry = ttk.Entry(self.vk_frame, width=100)
        self.id_label = ttk.Label(self.vk_frame, text="ID пользователя:")
        self.id_entry = ttk.Entry(self.vk_frame, width=50)
        self.album_label = ttk.Label(self.vk_frame, text="Выберите альбом:")
        self.combobox_value = tk.StringVar()
        self.album_combobox = ttk.Combobox(self.vk_frame, height=4, textvariable=self.combobox_value, state="readonly")
        self.count_foto_label = ttk.Label(self.vk_frame, text="Количество фото в запросе:")
        self.count_foto_spinbox = tk.Spinbox(self.vk_frame, from_=1, to=100, width=5, justify=tk.RIGHT)
        self.vk_button = tk.Button(self.vk_frame, text="Отправить запрос", command=self.get_vk_info)

        self.vk_info_frame = ttk.LabelFrame(self.window, text="Результат запроса из ВКонтакте", relief=tk.RIDGE)
        self.vk_info_label = ttk.Label(self.vk_info_frame, text="Здесь отобразиться результат запроса")

        self.vk_foto_frame = ttk.LabelFrame(self.window, text="ФОТО из ВКонтакте", relief=tk.RIDGE)
        self.vk_foto_name = ttk.LabelFrame(self.vk_foto_frame, text="Имя файла ФОТО", relief=tk.RIDGE)
        self.vk_prev_button = tk.Button(self.vk_foto_name, text="ФОТО <<<", command=self.get_prev_foto)
        self.vk_next_button = tk.Button(self.vk_foto_name, text=">>> ФОТО", command=self.get_next_foto)
        self.vk_choice_button = tk.Button(self.vk_foto_name, text="Выбрать текущее ФОТО", command=self.get_choice_foto)
        self.vk_choice_all_button = tk.Button(self.vk_foto_name, text="Выбрать все ФОТО", command=self.get_choice_all_foto)
        self.vk_foto_listbox = tk.Listbox(self.vk_foto_name, selectmode='single', width=30)

        self.vk_foto = ttk.LabelFrame(self.vk_foto_frame, text="Миниатюра текущего ФОТО", relief=tk.RIDGE)
        self.vk_foto_label = Label(self.vk_foto, height=300, width=300)
        self.vk_foto_filename_label = ttk.Label(self.vk_foto)

        self.yd_foto_frame = ttk.LabelFrame(self.window, text="Выбранные ФОТО", relief=tk.RIDGE)
        self.yd_foto_listbox = tk.Listbox(self.yd_foto_frame, selectmode='single', width=30)
        self.yd_del_button = tk.Button(self.yd_foto_frame, text="Удалить из списка", command=self.del_foto)

        self.yd_frame = ttk.LabelFrame(self.window, text="Для загрузки на Яндекс.Диск", relief=tk.RIDGE)
        self.yd_token_label = ttk.Label(self.yd_frame, text="Ключ авторизации:")
        self.yd_token_entry = ttk.Entry(self.yd_frame, width=100)
        self.yd_path_label = ttk.Label(self.yd_frame, text="Папка на Яндекс.Диске:")
        self.yd_path_entry = ttk.Entry(self.yd_frame, width=50)
        self.yd_button = tk.Button(self.yd_frame, text="Загрузить на Яндекс.Диск", command=self.upload)

        self.log_frame = ttk.LabelFrame(self.window, text="Лог процессов", relief=tk.RIDGE)
        self.log_text = tk.Text(self.log_frame, height=5, width=30)
        self.log_button = tk.Button(self.log_frame, text="Сохранить лог", command=self.save_log)


        self.create_widgets()

    # Функция создания главном окна и виджетов
    def create_widgets(self):
        self.window['padx'] = 5
        self.window['pady'] = 5

        # Создание фрейма исходных данных для запроса Вконтакте
        self.vk_frame.config(text="Исходные данные для запроса ВКонтакте", relief=tk.RIDGE)
        self.vk_frame.grid(row=1, column=1, sticky=tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

        self.token_label.config(text="Ключ к API:")
        self.token_label.grid(row=1, column=1, sticky=tk.W + tk.N, padx=5, pady=5)

        # global token_entry
        # token_entry = ttk.Entry(vk_frame, width=100)
        self.token_entry.grid(row=1, column=2, sticky=tk.W, padx=5, pady=3)
        self.token_entry.insert(tk.END, "")

        # id_label = ttk.Label(vk_frame, text="ID пользователя:")
        self.id_label.grid(row=2, column=1, sticky=tk.W + tk.N, padx=5, pady=5)

        # global id_entry
        # id_entry = ttk.Entry(vk_frame, width=50)
        self.id_entry.grid(row=2, column=2, sticky=tk.W, padx=5, pady=3)
        self.id_entry.insert(tk.END, "")

        # album_label = ttk.Label(vk_frame, text="Выберите альбом:")
        self.album_label.grid(row=3, column=1, sticky=tk.W + tk.N, padx=5, pady=5)

        # self.combobox_value = tk.StringVar()
        # global album_combobox
        # album_combobox = ttk.Combobox(vk_frame, height=4, textvariable=self.combobox_value, state="readonly")
        self.album_combobox.grid(row=3, column=2, sticky=tk.W, padx=5, pady=3)
        self.album_combobox['values'] = ("wall", "profile", "saved")
        self.album_combobox.current(1)

        # count_foto_label = ttk.Label(vk_frame, text="Количество фото в запросе:")
        self.count_foto_label.grid(row=4, column=1, sticky=tk.W + tk.N, padx=5, pady=5)

        vcmd = (self.window.register(self.validate_spinbox), '%P')
        # global count_foto_spinbox
        # count_foto_spinbox = tk.Spinbox(vk_frame, from_=1, to=100, width=5, justify=tk.RIGHT)
        self.count_foto_spinbox.grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        self.count_foto_spinbox.delete(0, tk.END)
        self.count_foto_spinbox.insert(1, "5")
        self.count_foto_spinbox.configure(validate="key", validatecommand=vcmd)

        # vk_button = tk.Button(vk_frame, text="Отправить запрос", command=self.get_vk_info)
        self.vk_button.grid(row=4, column=2, padx=5, pady=5, sticky=tk.E)

        # Создание фрейма результата запроса информации о профиле из ВКонтакте
        # vk_info_frame = ttk.LabelFrame(self.window, text="Результат запроса из ВКонтакте", relief=tk.RIDGE)
        self.vk_info_frame.grid(row=1, column=2, sticky=tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

        # Создание фрейма результата запроса информации о фотографиях в профиле ВКонтакте
        # global vk_info_label
        # vk_info_label = ttk.Label(vk_info_frame, text="Здесь отобразиться результат запроса")
        self.vk_info_label.grid(row=2, column=1, sticky=tk.W + tk.N, padx=5, pady=5)

        # global vk_foto_frame
        # vk_foto_frame = ttk.LabelFrame(self.window, text="ФОТО из ВКонтакте", relief=tk.RIDGE)
        self.vk_foto_frame.grid(row=2, column=1, sticky=tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

        # global vk_foto_name
        # vk_foto_name = ttk.LabelFrame(vk_foto_frame, text="Имя файла ФОТО", relief=tk.RIDGE)
        self.vk_foto_name.grid(row=1, column=1, sticky=tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

        # vk_prev_button = tk.Button(vk_foto_name, text="ФОТО <<<", command=self.get_prev_foto)
        self.vk_prev_button.grid(row=1, column=1, padx=5, pady=5)

        # vk_next_button = tk.Button(vk_foto_name, text=">>> ФОТО", command=self.get_next_foto)
        self.vk_next_button.grid(row=1, column=2, padx=5, pady=5)

        # vk_choice_button = tk.Button(vk_foto_name, text="Выбрать текущее ФОТО", command=self.get_choice_foto)
        self.vk_choice_button.grid(row=4, column=1, padx=5, pady=5, columnspan=2)

        # vk_choice_all_button = tk.Button(vk_foto_name, text="Выбрать все ФОТО", command=self.get_choice_all_foto)
        self.vk_choice_all_button.grid(row=5, column=1, padx=5, pady=5, columnspan=2)

        # global vk_foto
        # vk_foto = ttk.LabelFrame(vk_foto_frame, text="Миниатюра текущего ФОТО", relief=tk.RIDGE)
        self.vk_foto.grid(row=1, column=2, sticky=tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

        # global vk_foto_label
        # vk_foto_label = Label(vk_foto, height=300, width=300)
        # global vk_foto_filename_label
        # vk_foto_filename_label = ttk.Label(vk_foto)

        # global vk_foto_listbox
        # vk_foto_listbox = tk.Listbox(vk_foto_name, selectmode='single', width=30)
        self.vk_foto_listbox.grid(row=2, column=1, sticky=tk.E + tk.W + tk.N + tk.S, padx=5, pady=5, columnspan=2)

        # Создание фрейма списка выбранных для загрузки на ЯндексДиск фотографий
        # yd_foto_frame = ttk.LabelFrame(self.window, text="Выбранные ФОТО", relief=tk.RIDGE)
        self.yd_foto_frame.grid(row=2, column=2, sticky=tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

        # global yd_foto_listbox
        # yd_foto_listbox = tk.Listbox(yd_foto_frame, selectmode='single', width=30)
        self.yd_foto_listbox.grid(row=1, column=1, sticky=tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

        # yd_del_button = tk.Button(yd_foto_frame, text="Удалить из списка", command=self.del_foto)
        self.yd_del_button.grid(row=2, column=1, padx=5, pady=5)

        # Создание фрейма для работы с API ЯндексДиска
        # yd_frame = ttk.LabelFrame(self.window, text="Для загрузки на Яндекс.Диск", relief=tk.RIDGE)
        self.yd_frame.grid(row=4, column=1, sticky=tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

        # yd_token_label = ttk.Label(yd_frame, text="Ключ авторизации:")
        self.yd_token_label.grid(row=1, column=1, sticky=tk.W + tk.N, padx=5, pady=5)

        # global yd_token_entry
        # yd_token_entry = ttk.Entry(yd_frame, width=100)
        self.yd_token_entry.grid(row=1, column=2, sticky=tk.W, padx=5, pady=3)
        self.yd_token_entry.insert(tk.END, "")

        # yd_path_label = ttk.Label(yd_frame, text="Папка на Яндекс.Диске:")
        self.yd_path_label.grid(row=2, column=1, sticky=tk.W + tk.N, padx=5, pady=5)

        # global yd_path_entry
        # yd_path_entry = ttk.Entry(yd_frame, width=50)
        self.yd_path_entry.grid(row=2, column=2, sticky=tk.W, padx=5, pady=3)
        self.yd_path_entry.insert(tk.END, "ФОТО из ВК")

        # yd_button = tk.Button(yd_frame, text="Загрузить на Яндекс.Диск", command=self.upload)
        self.yd_button.grid(row=3, column=2, padx=5, pady=5, sticky=tk.E)

        # Создание фрейма для отображения лога процессов приложения
        # log_frame = ttk.LabelFrame(self.window, text="Лог процессов", relief=tk.RIDGE)
        self.log_frame.grid(row=4, column=2, sticky=tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

        # global log_text
        # log_text = tk.Text(log_frame, height=5, width=30)
        self.log_text.grid(row=1, column=1)

        # log_button = tk.Button(log_frame, text="Сохранить лог", command=self.save_log)
        self.log_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)

    # Функция проверки ввода символов при выборе количества фотографий (разрешены только цифры)
    def validate_spinbox(self, new_value):
        return new_value.isdigit()

    # Функция сохранения лога процессов приложения в файл
    def save_log(self):
        if len(program.log_text.get('1.0', tk.END)) > 1:
            log_file_name = datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S')
            self.set_log_string(f'Сохранение лога в файл {log_file_name}.txt\n')
            with open(f'log/{log_file_name}.txt', 'w') as f:
                for log_str in program.log_text.get('1.0', tk.END):
                    f.write(log_str)
            dial = MyDialog("FOTO_from_VK_to_YD",
                            f'Лог сохранен в файл: log/ {log_file_name}.txt')
            dial.show_text()
        else:
            dial = MyDialog("FOTO_from_VK_to_YD", "Лог программы пустой")
            dial.show_text()
        return

    # Функция добавления строки в лог процессов
    def set_log_string(self, log_string):
        self.log_text.insert(tk.END, log_string)
        self.log_text.see(tk.END)
        return

    # Функция обработки нажатия кнопки - предыдущее фото
    def get_prev_foto(self):
        if self.vk_foto_listbox.index('active') > 0:
            getval_index = self.vk_foto_listbox.index('active')
            self.vk_foto_listbox.select_clear(getval_index)
            self.vk_foto_listbox.select_set(getval_index - 1)
            self.vk_foto_listbox.activate(getval_index - 1)
            getval_text = self.vk_foto_listbox.get('active')
            self.get_foto(getval_text)

    # Функция обработки нажатия кнопки - следующее фото
    def get_next_foto(self):
        if self.vk_foto_listbox.index('active') < self.vk_foto_listbox.size() - 1:
            getval_index = self.vk_foto_listbox.index('active')
            self.vk_foto_listbox.select_clear(getval_index)
            self.vk_foto_listbox.select_set(getval_index + 1)
            self.vk_foto_listbox.activate(getval_index + 1)
            getval_text = self.vk_foto_listbox.get('active')
            self.get_foto(getval_text)

    # Функция обработки нажатия кнопки - добавить текущее фото в список загрузки
    def get_choice_foto(self):
        if self.vk_foto_listbox.index('active') >= 0:
            if self.vk_foto_listbox.get('active') not in self.yd_foto_listbox.get(0, tk.END):
                self.yd_foto_listbox.insert(tk.END, self.vk_foto_listbox.get('active'))
                self.yd_foto_listbox.select_set(tk.END)
                self.yd_foto_listbox.activate(tk.END)
        return

    # Функция обработки нажатия кнопки - добавить все фото в список загрузки
    def get_choice_all_foto(self):
        if self.vk_foto_listbox.size() > 0:
            for i in range(len(self.vk_foto_listbox.get(0, tk.END))):
                self.yd_foto_listbox.insert(tk.END, self.vk_foto_listbox.get(0, tk.END)[i])
            self.yd_foto_listbox.select_set(tk.END)
            self.yd_foto_listbox.activate(tk.END)
        return

    # Функция обработки нажатия кнопки - удалить фото из списка загрузки
    def del_foto(self):
        if len(self.yd_foto_listbox.get(0, tk.END)) > 0 and self.yd_foto_listbox.index('active') >= 0:
            self.yd_foto_listbox.delete('active')
            self.yd_foto_listbox.select_set(tk.END)
            self.yd_foto_listbox.activate(tk.END)
        return

    # Функция отображения фотографий при навигации по списку фотографий
    def get_foto(self, file_name):
        img = Image.open(f'images/{file_name}')
        img.thumbnail((300, 300))

        tatras = ImageTk.PhotoImage(img)
        self.vk_foto_label.config(image='')
        self.vk_foto_label.config(image=tatras)

        self.vk_foto_label.image = tatras
        self.vk_foto_label.pack()

        self.vk_foto_filename_label.config(text=file_name)
        self.vk_foto_filename_label.pack()

    # Функция обработки нажатия кнопки - обработка запроса ВКонтакте
    def get_vk_info(self):

        self.set_log_string(f'Старт запроса: {datetime.datetime.now()}\n')
        self.set_log_string(f'ID пользователя в ВК: {self.id_entry.get()}\n')

        # Создаем экземпляр объекта класса VK
        vk = VK(self.token_entry.get())

        # Сохраняем результат запроса информации о профиле в список
        dict_user_info = vk.users_info(self.id_entry.get())
        self.set_log_string(f'Профиль: {"Закрытый" if dict_user_info['response'][0]['is_closed'] else "Открытый"}\n')
        self.set_log_string(f'Просмотр профиля: {"Возможен" if dict_user_info['response'][0]['can_access_closed'] else "Не возможен"}\n')

        self.vk_info_label.config(text=(f'ID пользователя: {dict_user_info['response'][0]['id']}\n'
                                   f'Имя пользователя: {dict_user_info['response'][0]['first_name']}\n'
                                   f'Фамилия пользователя: {dict_user_info['response'][0]['last_name']}\n'
                                   f'Профиль: {"Закрытый" if dict_user_info['response'][0]['is_closed'] else "Открытый"}'))

        # Если доступ к профилю возможен, то запрашиваем информацию о фотографиях
        if dict_user_info['response'][0]['can_access_closed']:
            # Сохраняем результат запроса информации о профиле в список
            dict_user_foto = vk.get_photos(self.id_entry.get(), count=self.count_foto_spinbox.get())
            # Если доступ к альбому возможен, то...
            if 'error' not in dict_user_foto:
                # Если в альбоме есть фотографии, то...
                if dict_user_foto['response']['count'] > 0:
                    self.set_log_string(f'Количество фото в профиле: {dict_user_foto['response']['count']}\n')
                    self.set_log_string(f'В запросе: {self.count_foto_spinbox.get()} фотографий\n')
                    self.vk_foto_frame.config(text=f'ФОТО из ВКонтакте - Альбом: "{self.album_combobox.get()}". '
                                              f'Количество фото в профиле: {dict_user_foto['response']['count']}, '
                                              f'запрошено {self.count_foto_spinbox.get()} фото')
                    list_url = []
                    list_filename = []
                    self.vk_foto_listbox.delete(0, tk.END)
                    self.yd_foto_listbox.delete(0, tk.END)
                    self.yd_foto_listbox.activate(tk.END)
                    # Цикл проверки словарей для поиска нужного URL-адреса фотографии
                    for dict in dict_user_foto['response']['items']:
                        # Если в текущем словаре нет ключа - orig_photo, то выбираем по ключу - type
                        if 'orig_photo' not in dict:
                            my_url = ""
                            size_list = ['','','','','','','','','','']

                            for size in dict['sizes']:
                                match size['type']:
                                    case 'w': size_list[0] = size['url']
                                    case 'z': size_list[1] = size['url']
                                    case 'y': size_list[2] = size['url']
                                    case 'x': size_list[3] = size['url']
                                    case 'r': size_list[4] = size['url']
                                    case 'q': size_list[5] = size['url']
                                    case 'p': size_list[6] = size['url']
                                    case 'o': size_list[7] = size['url']
                                    case 'm': size_list[8] = size['url']
                                    case 's': size_list[9] = size['url']

                            for i in range(10):
                                if size_list[i] != '':
                                    my_url = size_list[i]
                                    break
                        else:
                            my_url = dict['orig_photo']['url']
                        # Выполняем запрос по выбранному адресу
                        response = requests.get(my_url)
                        if response.status_code == 200:
                            list_url.append(my_url)
                            self.set_log_string(f'Ссылка на фото: {my_url}\n')
                            self.set_log_string(f'Дата и время загрузки фото:'
                                                f' {datetime.datetime.fromtimestamp(int(dict['date'])).strftime('%Y-%m-%d %H_%M_%S')}\n')
                            self.set_log_string(f'Количество лайков фото: {dict['likes']['count']}\n')
                            my_filename = (f'{datetime.datetime.fromtimestamp(int(dict['date'])).strftime('%Y-%m-%d %H_%M_%S')}'
                                           f'_{dict['likes']['count']}.jpg')
                            list_filename.append(my_filename)
                            # Сохраняем фото в папку на локальном компьютере
                            with open(f'images/{my_filename}', 'wb') as f:
                                f.write(response.content)
                            self.set_log_string(f'Фото сохранено в файл: images/{my_filename}\n')
                            self.vk_foto_listbox.insert(tk.END, my_filename)
                        else:
                            self.set_log_string(f'Фото по ссылке: {my_url} не найдено!\n')
                            self.set_log_string(f'Ответ сервера [{response.status_code}]: {response.text}\n')
                            dial = MyDialog("FOTO_from_VK_to_YD",
                                            f'Фото по ссылке не найдено!')
                            dial.show_text()
                    self.vk_foto_listbox.select_set(0)
                    self.get_foto(list_filename[0])
                else:
                    self.vk_foto_frame.config(
                        text=f'ФОТО из ВКонтакте - Альбом: "{self.album_combobox.get()}". В выбранном альбоме НЕТ фото!')
            else:
                dial = MyDialog("FOTO_from_VK_to_YD",
                                f'Операция не выполнена. '
                                f'Сообщение: {dict_user_foto.get("error", {}).get("error_msg")}')
                dial.show_text()
        return

    # Функция обработки нажатия кнопки - загрузить на ЯндексДиск
    def upload(self):
        # Создаем папку для сохранения фото
        yd_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': self.yd_path_entry.get()}
        headers = {'Authorization': f'OAuth {self.yd_token_entry.get()}'}
        response = requests.put(yd_url, params=params, headers=headers)

        if response.status_code == 201:
            self.set_log_string(f'Ответ сервера [201]: {response.text}\n')
        elif response.status_code == 409:
            self.set_log_string(f'Ответ сервера [409]: {response.text}\n')

        json_data = []
        # Для каждой фотографии добавленной в список загрузки...
        for name in self.yd_foto_listbox.get(0, tk.END):
            # Формируем строку запроса
            upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            params = {'path': f'{self.yd_path_entry.get()}/{name}'}
            response = requests.get(upload_url, params=params, headers=headers)
            # Проверяем есть ли на ЯндексДиске файл с таким же именем
            if response.status_code == 200:
                self.set_log_string(f'Ответ сервера [200]: {response.text}\n')
                url_for_upload = response.json()['href']
                with open(f'images/{name}', 'rb') as f:
                    requests.put(url_for_upload, files={'file': f})
                self.set_log_string(f'Фото: {name} загружено в папку {self.yd_path_entry.get()} на Яндекс.Диске\n')
                # Записываем в список json-информацию о загруженном файле
                (json_data.append({"file_name": name, "size": os.stat(f'images/{name}').st_size}))
            elif response.status_code == 409:
                self.set_log_string(f'Ответ сервера [409]: {response.text}\n')
                dial = MyDialog("FOTO_from_VK_to_YD",
                                f'Фото {name } уже существует на сервере в папке {self.yd_path_entry.get()}')
                dial.show_text()
        # Сохраняем json-файл на локальном компьютере
        json_filename = f'json/{datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S')}_result.json'
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False)
        self.set_log_string(f'Отчёт: {json_filename} сохранен\n')

        dial = MyDialog("FOTO_from_VK_to_YD", "Текущая операция завершена")
        dial.show_text()
        return

if __name__ == '__main__':
    # Создаем экземпляр класса графической оболочки приложения
    program = Counter_program()
    # Отображаем главное окно приложения
    program.window.mainloop()



