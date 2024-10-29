import socket
import os
import threading
from datetime import datetime
from pathlib import Path
import random
import cv2

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import OpenAIEmbeddings
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from DialogManager import DialogManager

import chromadb
from openai import OpenAI
import time
from pygame import mixer
from ElmoV2API import ElmoV2API
from deepface import DeepFace
from face_recognizer import recognize, store_new_user

storage_path = "/your/path/here"

client = chromadb.PersistentClient(path=storage_path)
speech_client = OpenAI(default_headers={"OpenAI-Beta": "assistants=v2"})

os.environ["OPENAI_API_KEY"] = "key_here"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "key_here"

llm = ChatOpenAI(model="gpt-4-turbo-2024-04-09", temperature=1)
llm_eval = ChatOpenAI(model="gpt-4-turbo-2024-04-09")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1024)

mixer.init()

debug = True

def generate_tts(sentence, speech_file_path):
    response = speech_client.audio.speech.create(model="tts-1", voice="echo", input=sentence)
    response.stream_to_file(speech_file_path)
    return str(speech_file_path)

def play_sound(file_path):
    mixer.music.load(file_path)
    mixer.music.play()

def TTS(text):
    speech_file_path = generate_tts(text, "speech.mp3")
    play_sound(speech_file_path)
    while mixer.music.get_busy():
        time.sleep(1)
    mixer.music.unload()
    ret = os.remove(speech_file_path)
    return ret


def recv_full_msg(sock, buffer_size=4096):
    data = ""
    speaking = False
    i = 0
    while True:
        try:
            part = sock.recv(buffer_size).decode()
            if debug:
                print(f"RECEIVED PART: {part}")
            if not part:
                break
            elif i == 0:
                i=1
            elif "STARTEND" in part:
                data = ""
                speaking = False
            elif part == "END":
                if data:
                    break
                speaking = False
                continue
            elif part == "START":
                speaking = True
            else:
                if part[-1] == ".":
                    data += part[:-1] + " "
                else:
                    data += part
        except socket.timeout:
            continue  # Continue receiving until we get the full message
    return data

def retrieve_list_users():
    with open("users_memory.txt", "r") as file:
        data = file.read()
        memory_users = data.split()

    with open("users_no_memory.txt", "r") as file:
        data = file.read()
        no_memory_users = data.split()

    if not memory_users:
        memory_users = []
    if not no_memory_users:
        no_memory_users = []

    return memory_users, no_memory_users

def decide_memory(user_id, new, memory_users, no_memory_users):
    if new:
        if len(memory_users) <= len(no_memory_users):
            with open("users_memory.txt", "a") as file:
                file.write(f"{user_id}\n")
            return True
        else:
            with open("users_no_memory.txt", "a") as file:
                file.write(f"{user_id}\n")
            return False
    else:
        if user_id in memory_users:
            return True
        else:
            return False

def add_interaction(id, new, flag):
    if new:
        if flag:
            with open(f"form_ids/memory/{id}.txt", "w") as f:
                f.write("")
        else:
            with open(f"form_ids/no_memory/{id}.txt", "w") as f:
                f.write("")
    else:
        if flag:
            with open(f"form_ids/memory/{id}.txt", "a") as f:
                f.write("\n")
        else:
            with open(f"form_ids/no_memory/{id}.txt", "a") as f:
                f.write("\n")

def main_handler(robot):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 8080

    print("Server started!")
    print("Waiting for clients...")

    s.bind((host, port))
    s.listen(5)
    c, addr = s.accept()

    memory_users, no_memory_users = retrieve_list_users()
    if debug:
        print(memory_users, no_memory_users)
    robot.set_screen(image="normal.png")
    uname = None

    while True:
        form_id = input("ID? \n> ")
        new = input("First time?\n> ")
        if new == "y":
            uname = input("User name?\n> ")
            user_id = store_new_user(robot, debug)
            with open(f"first_names/{user_id}.txt", "w") as f:
                f.write(f"{uname}")
            new = True
        else:
            new, user_id = recognize(robot, debug)
            while new is None:
                new, user_id = recognize(robot, debug)
                time.sleep(1)
            if new == "confirm":
                with open(f"first_names/{user_id}.txt", "r") as f:
                    uname = f.read()
                ret = TTS(f"Is {uname} your name? Please respond with yes or no")
                try:
                    user_msg = recv_full_msg(c) # receive response
                except socket.error:
                    break
                if "yes" in user_msg or "Yes" in user_msg:
                    new = False
                else:
                    user_id = store_new_user(robot)
                    new = True

        flag = decide_memory(user_id, new, memory_users, no_memory_users)
        if new:
            if flag:
                memory_users += [user_id,]
            else:
                no_memory_users += [user_id,]
        else:
            with open(f"first_names/{user_id}.txt", "r") as f:
                uname = f.read()
        if debug:
            print(f"Memory? -> {flag}")

        if flag:
            user_db = client.get_or_create_collection(name=user_id)
            dm = DialogManager(user_id, uname, llm, llm_eval, user_db, new, flag, debug)
        else:
            dm = DialogManager(user_id, uname, llm, llm_eval, None, new, flag, debug)

        elmo_msg = dm.greeting_message()
        ret = TTS(elmo_msg)
        while True:
            try:
                user_msg = recv_full_msg(c) # receive response
            except socket.error:
                break
            if not user_msg:
                continue
            if debug:
                print(user_msg)
            robot.set_screen(image="thinking.png")
            elmo_msg, ext_code = dm.eval(user_msg)
            robot.set_screen(image="normal.png")
            ret = TTS(elmo_msg)
            if ext_code:
                break

        dm.generate_user_info()
        add_interaction(form_id, new, flag)

if __name__ == "__main__":
    robot = ElmoV2API("192.168.0.102", False)
    # on start
    """robot.set_volume(50)
    robot.enable_behavior(name="look_around", control=False)
    robot.set_tilt_torque(True)
    robot.set_pan_torque(True)
    robot.set_tilt(0)
    robot.set_pan(0)
    robot.set_tilt(-5)"""
    if debug:
        print(robot.status())
    main_handler(robot)
