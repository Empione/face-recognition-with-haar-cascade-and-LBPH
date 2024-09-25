import PySimpleGUI as sg
import face_recognition_model
import time
import os
import webbrowser
from datetime import datetime as dt
import shutil

try:
    dict_id_name = face_recognition_model.read_id_name()
except:
    dict_id_name = {}
    face_recognition_model.write_id_name(dict_id_name)

sg.theme('BlueMono')

url = 'https://github.com/Empione/face_recognition_rdk'

font_url = ('Courier New', 10, 'underline')
font = ('Courier New', 12)
path = './faces_image'

layout = [[sg.Text('   Это приложение разработано в рамках выпускной квалификационной работы магистра\n'
                   'для тестирования биометрической аутентификации методом распознавания лиц\n'
                   'с использованием алгоритмов: \n'
                   ' - "каскад Хаара" для обнаружения лиц,\n'
                   ' - гистограммы локальных бинарных шаблонов (LBPH) для идентификации лиц.', font=font)],
          [sg.T('')],
          [sg.Text('Ссылка на проект в репозитории github:', font=('Courier New', 10),
                   justification='right', size=(50, 1)),
           sg.Text(url, tooltip=url, enable_events=True, font=font_url, key=f'URL {url}')],
          [sg.T('')],
          [sg.Button('Вход', size=(10, 1), )]
          ]

add_column = [[sg.Text('Для добавления нового пользователя '
                       '\nнеобходимо ввести: ID и имя пользователя.',
                       background_color='#d3dfda')],
              [sg.Text('ID', size=(9, 1)), sg.Text('Имя', size=(10, 1))],
              [sg.InputText(key='-ID-', size=(10, 1)),
               sg.InputText(key='-NAME-', size=(20, 1)),
               sg.Submit('Добавить')]
              ]

output_column = [[sg.Text('Окно отображения работы программы.',
                          background_color='#d3dfda')],
                 [sg.Output(size=(77, 8))]
                 ]

recognition_column = [[sg.Text('Тестирование процесса идентификации '
                               '\nпользователя.',
                               background_color='#d3dfda', size=(30, 2))],
                      [sg.T('', background_color='#d3dfda', size=(10, 1)), sg.Button('Идентифицировать пользователя')]
                      ]

remove_column = [[sg.Text('Для удаления пользователя из базы'
                          '\nнеобходимо ввести его ID.',
                          background_color='#d3dfda')],
                 [sg.Text('ID', size=(9, 1))],
                 [sg.InputText(key='-ID2-', size=(10, 1)), sg.Text(size=(10, 1), background_color='#d3dfda'),
                  sg.Submit('Удалить')]
                 ]

layout2 = [[sg.Column(add_column, background_color='#d3dfda'),
            sg.Column(remove_column, background_color='#d3dfda')],
           [sg.Column(recognition_column, background_color='#d3dfda')],
           [sg.T('')],
           [sg.Column(output_column, background_color='#d3dfda')],
           [sg.T('')],
           [sg.Button('Выход', size=(10, 1))]
           ]

# Отображение окна
window = sg.Window('Программа для тестирования биометрической аутентификации',
                   layout, element_justification='c')
while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break
    elif event.startswith("URL "):
        webbrowser.open(url)
    elif event == 'Вход':
        window.close()
        window = sg.Window('Основной модуль программы', layout2)
        while True:
            event, values = window.read()
            if event in (None, 'Exit', 'Выход'):
                window.close()
                break
            elif event == 'Добавить':
                if (values['-ID-'] and values['-NAME-']) != '':
                    ID = values['-ID-']
                    NAME = values['-NAME-']
                    if ID not in dict_id_name.keys():
                        os.mkdir(path + '/user_{}#{}'.format(NAME, ID))
                        print("[INFO] Инициализация захвата лица. Смотрите в камеру…\n")
                        dict_id_name.update({ID: NAME})
                        face_recognition_model.write_id_name(dict_id_name)
                        for i in range(3, 0, -1):
                            time.sleep(1)
                            print("{}...".format(i))
                        face_recognition_model.create(ID)
                        print('\n[INFO] Программа сбора изображений лица пользователя завершена.\n')
                        print('[INFO] Начало обработки изображений. Подождите...\n')
                        start_time = time.time()
                        face_recognition_model.train()
                        end_time = time.time() - start_time
                        filelist = []
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                filelist.append(os.path.join(root, file))
                        with open('log_authentication.txt', 'a+') as log:
                            date = dt.now()
                            date_split = date.strftime("[%Y-%m-%d %H:%M:%S]")
                            log.write('{}: new user {}#{} has been added.\n'.format(date_split, NAME, ID))
                        print("[INFO] Программа обработки изображений завершена успешна. "
                              "\n   - Время для обработки {} изображений "
                              "составило {} \n".format(len(filelist), round(end_time, 2)))
                    else:
                        print("[INFO] Пользователь с таким ID уже существует.\n")
                else:
                    print('[INFO] Не указан индификатор или имя пользователя...\n')
            elif event == 'Идентифицировать пользователя':
                try:
                    face_recognition_model.recognitions()
                except:
                    print("[INFO] Отсутствует модель распознования.\n")
            elif event == 'Удалить':
                if values['-ID2-'] != '':
                    ID = values['-ID2-']
                    if ID in dict_id_name.keys():
                        shutil.rmtree(path + '/user_{}#{}'.format(dict_id_name.get(ID), ID))
                        with open('log_authentication.txt', 'a+') as log:
                            date = dt.now()
                            date_split = date.strftime("[%Y-%m-%d %H:%M:%S]")
                            log.write('{}: user {}#{} has been deleted.\n'.format(date_split,
                                                                               dict_id_name.get(ID), ID))
                        print("[INFO ]Начало процесса удаления пользователя. Подождите...\n")
                        try:
                            face_recognition_model.train()
                            print('[INFO] Пользователь {} успешно удален.\n'.format(dict_id_name.pop(ID)))
                            face_recognition_model.write_id_name(dict_id_name)
                        except:
                            os.remove('face.yml')
                            print('[INFO] Пользователь {} успешно удален.\n'.format(dict_id_name.pop(ID)))
                            face_recognition_model.write_id_name(dict_id_name)
                            print('[INFO] База пользователей пуста.\n')
                    else:
                        print('[INFO] Пользователь с таким ID отсутствует.\n')
                else:
                    print('[INFO] Не указан идентификатор...\n')

window.close()
