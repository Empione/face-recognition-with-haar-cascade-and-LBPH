import cv2
import numpy as np
import os
import json
import granting_access

conf_param = 40
N = 20 # Количество изображений пользователя
haar_cascade_path = ".\haarcascades\haarcascade_frontalface_default.xml"
recognizer = cv2.face.LBPHFaceRecognizer_create()

def write_id_name(dict_id_name):
    with open('dict_id_name.json', 'w') as name:
        name.write(json.dumps(dict_id_name))


def read_id_name():
    with open('dict_id_name.json', 'r') as name:
        dict_id_name = json.loads(str(name.read()))
    return dict_id_name

def read_names():
    with open('names.txt') as inp:
        names_array = inp.read().split(',')
    return names_array


def create(ID):
    dict = read_id_name()
    cascade = cv2.CascadeClassifier(haar_cascade_path)
    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    count = 0
    while True:
        ret, img = video_capture.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=6,
            minSize=(150, 150),
            maxSize=(250, 250)
        )
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            count += 1
            # Сохранение изображения лица.
            cv2.imwrite('./faces_image/user_{0}#{1}/ID_{1}'.format(dict.get(ID), ID)
                        + '.' + str(count) + '.jpg', gray[y:y + h, x:x + w])
        cv2.imshow('Cam', img)
        k = cv2.waitKey(1) & 0xff  # 'ESC'
        if k == 27:
            break
        # Завершение программы после создания N изображений пользователя.
        if count >= N:
            break
    video_capture.release()
    cv2.destroyAllWindows()


def train():

    def get_images_and_labels(path):
        full_image = []
        dir = os.listdir(path)
        for x in dir:
            image_path_array = [os.path.join(path + '/{}'.format(x), image_file)
                                for image_file in os.listdir(path + '/{}'.format(x))]
            full_image.extend(image_path_array)
        face_array = []   # Массив изображений лиц.
        ids = []    # Массив хранения id пользователей.
        for imp in full_image:
            img = cv2.imread(imp)
            # Перевод изображения в серый, тренер понимает только одноканальное изображение.
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_array.append(img)
            # Получение id из названия файла.
            id = int(os.path.split(imp)[-1].split("_")[1].split(".")[0])
            ids.append(id)
        return face_array, ids
    faces, ids = get_images_and_labels('./faces_image')
    # Обучение модели для идентификации.
    recognizer.train(faces, np.array(ids))
    # Сохранение полученного вектора признаков каждого пользователя.
    recognizer.write('face.yml')


def recognitions():
    flag = False
    dict_id_name = read_id_name()
    recognizer.read('face.yml')
    cascade = cv2.CascadeClassifier(haar_cascade_path)
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Список имен для id.
    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:
        ret, img = video_capture.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=6,
            minSize=(150, 150),
            maxSize=(250, 250)
        )
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
            # Пороговое значения для идентификации.
            if confidence < conf_param:
                name = dict_id_name.get(str(id))
                confidence = "  {0}%".format(round(100 - confidence))
                # flag = True
            else:
                name = "User unknown"
                confidence = "  {0}%".format(round(100 - confidence))
            cv2.putText(img, str(name), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
            if flag == True:
                granting_access.main(name, id)
        cv2.imshow('Cam', img)
        k = cv2.waitKey(1) & 0xff  # 'ESC'
        if k == 27 or flag == True:
            break
    video_capture.release()
    cv2.destroyAllWindows()
