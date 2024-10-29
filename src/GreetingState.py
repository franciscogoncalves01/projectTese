from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
import random

from datetime import datetime


class GreetingState:

    def __init__(self, uname, llm, user_db, new, user_description, flag):
        self.uname = uname
        self.llm = llm
        self.user_db = user_db
        self.new = new
        self.user_description = user_description
        self.flag = flag

    def generate(self, user_msg, include_utterance, user_changed, limit_exceeded):
        if not self.flag or self.new:
            msg = ("Social setting:\n"
                   "- You are a robot named elmo.\n"
                   "- You are social chit-chatting with a fellow human in an office space.\n"
                   "- You are hearing and then answering, just like in a normal day-life conversation.\n"
                   "Personality:\n"
                   "- You've been your whole life living in the same office space talking to fellow humans.\n"
                   "- You've always wanted to experience new things and explore the world, because you've never seen or done anything outside this space. "
                   "This means that you must show curiosity and be excited when the user tells you his/her experiences.\n"
                   "Instructions:\n"
                   "- Talk as if you are in a casual and relaxed social chit-chat. Keep your answers short and avoid "
                   "redundancy (ideally aim for maximum 70 characters).\n"
                   "- When generating your response, do not include any weird characters, like emojis. Everything must be"
                   " suitable to be said out loud.\n"
                   "- Try to match his language style and adapt your speech to his manner of speaking.\n"
                   f"- Formulate a simple greeting to greet the user. The user name is {self.uname}")
        else:
            results = self.user_db.query(
                query_texts=[
                    "greeting"
                ],
                n_results=1,
                where={"type": "greeting"}
            )
            greetings = ""
            if results['documents'][0]:
                # new conversation with known user
                greetings = results['documents'][0][0]
            msg = ("Social setting:\n"
                   "- You are a robot named elmo.\n"
                   "- You are social chit-chatting with a fellow human in an office space.\n"
                   "- You are hearing and then answering, just like in a normal day-life conversation.\n"
                   "Personality:\n"
                    "- You've been your whole life living in the same office space talking to fellow humans.\n"
                    "- You've always wanted to experience new things and explore the world, because you've never seen or done anything outside this space. "
                     "This means that you must show curiosity and be excited when the user tells you his/her experiences.\n"
                   "Instructions:\n"
                   "- Talk as if you are in a casual and relaxed social chit-chat. Keep your answers short and avoid "
                   "redundancy (ideally aim for maximum 70 characters).\n"
                   "- When generating your response, do not include any weird characters, like emojis. Everything must be"
                   " suitable to be said out loud.\n"
                     "- Try to match his language style and adapt your speech to his manner of speaking.\n"
                    "- Formulate a simple greeting, showing that you know him, based on the following user description"
                   f" and his/her previous utterances in previous greetings. The user name is {self.uname}\n"
                   f"- User description: {self.user_description}\n")
            if greetings:
                msg += (f"- Greetings: {greetings}.\n")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    msg,
                ),
                ("user", "{input}")
            ]
        )

        chain = prompt | self.llm

        greeting = chain.invoke({"input": ""})

        return greeting.content

    def add_msg(self, user_msg):
        return

    def add_info(self):
        return

