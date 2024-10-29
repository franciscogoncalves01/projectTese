import cv2
from deepface import DeepFace
import os
import numpy as np
import faiss
import time
import json
from datetime import datetime

def calculate_embedding(image, debug):
    # This function will compute the embedding for the given image using DeepFace
    try:
        result = DeepFace.represent(img_path=image, model_name="Facenet512")
        quant_users = len(result)
        if debug:
            print("THIS IS THE RESULT OF THE EMBEDDING")
            print(quant_users)
        return result[0]['embedding'], quant_users
    except Exception as e:
        print(f"Error during embedding calculation: {e}")
        return None, 0

def calculate_similarity(embedding1, embedding2):
    # Compute the dot product of the two embeddings
    dot_product = np.dot(embedding1, embedding2)

    # Compute the norms of the embeddings
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)

    # Compute the cosine similarity
    cosine_similarity = dot_product / (norm1 * norm2)

    return cosine_similarity

def recognize(robot, debug):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    if debug:
        print("waiting for face...")
    repeat_process = 0
    confirm_user = False
    almost_user = ["no user", 1]

    while repeat_process < 5:
        ret, screenshot = robot.grab_image()
        while ret != 200:
            ret, screenshot = robot.grab_image()
        screenshot_np = np.array(screenshot)
        frame = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        gray_screenshot = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_screenshot, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        has_face = len(faces) > 0

        # cv2.imshow('Screen Capture', frame)

        time.sleep(0.1)
        test_check = False
        if has_face:
            # Save the current frame to calculate its embedding
            frame_embedding, quant_users = calculate_embedding(frame, debug)
            if frame_embedding is None:
                if debug:
                    print("Error: Failed to compute embedding for the detected face.")
                if repeat_process == 0:
                    return None, ""
            else:
                if debug:
                    print("Found Face, I will do now the checkings")
                directory = "user_faces"
                for filename in os.listdir(directory):
                    f = os.path.join(directory, filename)
                    # checking if it is a file
                    user_embedding = np.load(f)
                    similarity = calculate_similarity(frame_embedding, user_embedding)
                    if debug:
                        print(f"Similarity Score with user {filename[:-4]}: ", similarity)

                    if similarity >= 0.55:
                        if debug:
                            print("User is very similiar")
                        if similarity < almost_user[1]:
                            almost_user = [filename[:-4], similarity]
                        confirm_user = True
                        if similarity >= 0.70:  # A threshold for confident match, adjust as needed
                            cv2.destroyAllWindows()
                            #write_logs(quant_users)
                            return False, filename[:-4]  # False means that the user is already registered
                repeat_process += 1

    if confirm_user:
        return False, almost_user[0]  # Confirm the user with the highest similarity

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    new_user_id = f"user_{formatted_datetime}"

    new_embedding, quant_users = calculate_embedding(frame, debug)

    embedding_path = f"user_faces/{new_user_id}.npy"
    # screenshot_name = f"user_faces/user_{new_user_id}.jpg"
    # cv2.imwrite(screenshot_name, frame)
    np.save(embedding_path, new_embedding)
    cv2.destroyAllWindows()

    #write_logs(quant_users)
    return True, new_user_id  # True means that the user is new

def store_new_user(robot, debug):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    while True:
        ret, screenshot = robot.grab_image()
        while ret != 200:
            ret, screenshot = robot.grab_image()
        screenshot_np = np.array(screenshot)
        frame = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        gray_screenshot = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_screenshot, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        has_face = len(faces) > 0

        # cv2.imshow('Screen Capture', frame)

        time.sleep(0.1)
        if has_face:
            new_embedding, quant_users = calculate_embedding(frame, debug)
            if new_embedding is None:
                continue
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            new_user_id = f"user_{formatted_datetime}"

            embedding_path = f"user_faces/{new_user_id}.npy"
            # screenshot_name = f"user_faces/user_{new_user_id}.jpg"
            # cv2.imwrite(screenshot_name, frame)
            np.save(embedding_path, new_embedding)
            cv2.destroyAllWindows()
            break

    return new_user_id
