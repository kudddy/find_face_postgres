import sys
import dlib
import cv2
import face_recognition
import os
import psycopg2
from tqdm import tqdm


def add_face(file_name):
    # Create a HOG face detector using the built-in dlib class
    face_detector = dlib.get_frontal_face_detector()

    # Load the image
    image = cv2.imread(file_name)

    # Run the HOG face detector on the image data
    detected_faces = face_detector(image, 1)

    print("Found {} faces in the image file {}".format(len(detected_faces), file_name))

 
    connection_db = psycopg2.connect("user='user' password='pass' host='localhost' dbname='db' port='5434'")
    db=connection_db.cursor()
    # Loop through each face we found in the image
    for i, face_rect in enumerate(detected_faces):
        # Detected faces are returned as an object with the coordinates
        # of the top, left, right and bottom edges
        print("- Face #{} found at Left: {} Top: {} Right: {} Bottom: {}".format(i, face_rect.left(), face_rect.top(),
                                                                                face_rect.right(), face_rect.bottom()))
        crop = image[face_rect.top():face_rect.bottom(), face_rect.left():face_rect.right()]
        encodings = face_recognition.face_encodings(crop)

        if len(encodings) > 0:
            query = "INSERT INTO vectors (file, vec_low, vec_high) VALUES ('{}', CUBE(array[{}]), CUBE(array[{}]));".format(
                file_name,
                ','.join(str(s) for s in encodings[0][0:63]),
                ','.join(str(s) for s in encodings[0][64:127]),
            )
            db.execute(query)
            print(query)
            connection_db.commit()
        cv2.imwrite("./.faces/aligned_face_{}_{}_crop.jpg".format(file_name.replace('/', '_'), i), crop)

    if connection_db is not None:
        connection_db.close()

IMAGE_TO_TRAIN = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'images')
IMAGE_INPUT_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'input')


def find_face(file_name):
    # Create a HOG face detector using the built-in dlib class
    face_detector = dlib.get_frontal_face_detector()

    # Load the image
    image = cv2.imread(file_name)

    # Run the HOG face detector on the image data
    detected_faces = face_detector(image, 1)

    print("Found {} faces in the image file {}".format(len(detected_faces), file_name))

    if not os.path.exists("./.faces"):
        os.mkdir("./.faces")

    connection_db = psycopg2.connect("user='user' password='pass' host='localhost' dbname='db' port='5434'")
    db=connection_db.cursor()

    # Loop through each face we found in the image
    for i, face_rect in enumerate(detected_faces):
        # Detected faces are returned as an object with the coordinates
        # of the top, left, right and bottom edges
        print("- Face #{} found at Left: {} Top: {} Right: {} Bottom: {}".format(i, face_rect.left(), face_rect.top(),
                                                                                face_rect.right(), face_rect.bottom()))
        crop = image[face_rect.top():face_rect.bottom(), face_rect.left():face_rect.right()]

        encodings = face_recognition.face_encodings(crop)
        if len(encodings) > 0:
            query = "SELECT file FROM vectors ORDER BY " + \
                    "(CUBE(array[{}]) <-> vec_low) + (CUBE(array[{}]) <-> vec_high) ASC LIMIT 1 ;".format(
                ','.join(str(s) for s in encodings[0][0:64]),
                ','.join(str(s) for s in encodings[0][64:128]),
            )
            db.execute(query)
            row = db.fetchone()

            while row is not None:
                print(row)
                row = db.fetchone()

            db.close()
        else:
            print("No encodings")

    if connection_db is not None:
        connection_db.close()


# добавляем енкодеры фотографий в базу
'''
for file_name in tqdm(os.listdir(IMAGE_TO_TRAIN)):
    full_path = os.path.join(IMAGE_TO_TRAIN,file_name)
    print(full_path)
    add_face(full_path)
'''

# ищем по фотографии
name = os.listdir(IMAGE_INPUT_PATH)[0]
full_path = os.path.join(IMAGE_INPUT_PATH, name)

find_face(full_path)

# Этапы работы приложения:
# 1. Юзер заходит в канал и ему предлагается нажать на start
# 2. Юзер нажимает на старт после чего он должен скинуть фото
# 3. На этом этапе сравниваем свежее фото и сравниваем с теми что уже есть
# Если фотография уже есть в базе, то достаем старую строку и отправляем сообщение
# Если же нет, то добавляем енкодер базу и стэкуем этот энкодер с уникальным идентификатор
# далее переходим к следующему шагу
# 4. Просим юзера ввести дату своего рождения


# модернизируем ф-цию для для работы в рамках бота
# схема базы данных
# (id serial, user_telegram_id varchar, message varchar, file varchar, vec_low cube, vec_high cube)