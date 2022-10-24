import os
import numpy as np
import cv2 as cv
import face_recognition as fr
import time

from numpy import ndarray

encoded = {}  # stores the users as keys and their encoded faces as values


def encode_picture(img):
    """
    Accepts as parameter a face-recognition image object, encodes it and returns
    the encoding.
    :param img: face-recognition image object
    :return: nd array of values, representing the encoded face.
    """
    face_locations = fr.face_locations(img)
    encoded_face = fr.face_encodings(img, face_locations)[0]
    return encoded_face


def take_picture():
    """
    Attempts ten times within 5 seconds to take a picture and find a face in it.
    If it succeeds, saves the picture in 'current_user_face' folder as current_user.jpg. Otherwise returns None.
    :return: None or np array
    """
    cap = cv.VideoCapture(available_cameras())

    for _ in range(10):
        time.sleep(0.5)
        # reading frame from camera
        success, frame = cap.read()
        # saving frame as a jpg file in prelim_image directory
        cv.imwrite('prelim_image/test.jpg', frame)
        prelim_image = fr.load_image_file('prelim_image/test.jpg')
        # delete the image from prelim_image directory
        os.remove('prelim_image/test.jpg')
        # finding a face in the image
        faces_locations = fr.face_locations(prelim_image)
        if faces_locations:
            # a face is found and the image is saved in current_user_face directory
            cv.imwrite('current_user_face/current_user.jpg', frame)
            cap.release()
            return prelim_image
    cap.release()
    return


def compare_encodings(encodings_list, encoding) -> ndarray[int]:
    """
    Compares the face encoding of the current user with the face encodings of known users.
    :param encodings_list: list of face encodings of known users.
    :param encoding: face encoding of current user.
    :return: the index of the matching face encoding in the encoded faces list of known users.
    """
    # a list of boolean values signalling the presence of a match
    match = fr.compare_faces(encodings_list, encoding)
    if any(match):
        face_distances = fr.face_distance(encodings_list, encoding)
        best_match_index = np.argmin(face_distances)
        return best_match_index


def available_cameras() -> int:
    """
    Checks if there are inbuilt of peripheral cameras on the user's computer.
    :return: int
    """
    cap = cv.VideoCapture(0)
    success, frame = cap.read()
    cap.release()
    if success:
        return 0
    cap = cv.VideoCapture(1)
    success, frame = cap.read()
    cap.release()
    if success:
        return 1


def get_encoded_faces() -> None:
    """
    Looks through the faces folder and encodes all
    the faces. Stores the values in the 'encoded' dictionary.
    :return: None
    """
    global encoded

    for dirpath, dnames, fnames in os.walk("./faces"):
        for f in fnames:
            image = fr.load_image_file("faces/" + f)
            face_locations = fr.face_locations(image)
            encoding = fr.face_encodings(image, face_locations)[0]
            encoded[f.split(".")[0]] = encoding


def run_facial_recognition() -> str:
    """
    Performs facial recognition.
    :return: the username of the current user if exists. Otherwise returns a string /useful for debugging/.
    """
    # gets the picture of the current user
    current_user_image = take_picture()
    if current_user_image is None:
        return 'Obtaining user image was unsuccessful.'
    # encodes the picture of the current user
    encoded_face = encode_picture(current_user_image)
    # fills the 'encoded' dictionary with the known users and their face encodings
    get_encoded_faces()
    if not encoded:
        return 'No user names present in memory'
    # gets the list of all known users
    usernames_list = list(encoded.keys())
    # gets the list of known users face encodings
    encodings_list = list(encoded.values())
    # matches the current user with the known users and gets the match index
    match_index = compare_encodings(encodings_list, encoded_face)
    if match_index is None:
        return 'No match found in known users list'
    current_user_name = usernames_list[match_index]
    os.remove('current_user_face/current_user.jpg')
    return current_user_name


def add_face_to_faces_folder(name: str) -> None:
    """
    Adds the picture of the current user to the faces folder.
    :param name: current username
    :return: None
    """
    # reads the image from the current_user_face directory
    image = cv.imread('current_user_face/current_user.jpg')
    # saves the image in the faces folder using the name argument
    cv.imwrite(f'faces/{name}.jpg', image)
    # removes the image from current_user_face directory
    os.remove('current_user_face/current_user.jpg')










