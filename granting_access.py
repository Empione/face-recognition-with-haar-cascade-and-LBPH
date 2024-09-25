from datetime import datetime as dt
import PySimpleGUI as sg


def main(id_name, id):
    sg.theme('BlueMono')
    font = ('Courier New', 12)
    with open('log_authentication.txt', 'a+') as log:
        date = dt.now()
        date_split = date.strftime("[%Y-%m-%d %H:%M:%S]")
        log.write('{}: user {}#{} was authenticated.\n'.format(date_split, id_name, id))

    layout = [[sg.T('')],
            [sg.Text('Пользователь {}#{} успешно авторизирован'.format(id_name, id), font=font)],
            [sg.T('')],
            [sg.Button('Ок', size=(10, 1), )]
            ]
    window = sg.Window('Предоставление доступа.',
                       layout, element_justification='c')
    while True:
        event, values = window.read()
        if event in (None, 'Exit'):
            break
        elif event == 'Ок':
            window.close()