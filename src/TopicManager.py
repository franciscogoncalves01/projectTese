from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
import random

from datetime import datetime

class TopicManager:

    def __init__(self, user_db, new, flag, debug):
        self.debug = debug
        self.user_db = user_db
        self.new = new
        self.flag = flag
        self.user_topics = self.get_topics()
        self.current_topics = []
        self.current_topic = "begin"

    def get_topics(self):
        if self.new or not self.flag:
            return []

        results = self.user_db.query(
            query_texts=[
                "topics"
            ],
            n_results=1,
            where={"type": "topics"}
        )
        if results['documents'][0]:
            res = results['documents'][0][0].split("\n")

            topics = []
            for topic in res:
                if topic != "":
                    topics += [topic,]
            if self.debug:
                print(topics)
            return topics
        else:
            return []

    def add_topic(self, topic):
        if self.debug:
            print(f"TOPIC MANAGER: Added new topic to current conversation: {topic}.")
        self.current_topic = topic
        if topic not in self.current_topics:
            self.current_topics += [topic,]

    def known_topics(self):
        return self.user_topics

    def choose_topic(self):
        topics = [t for t in self.user_topics if t not in self.current_topics]

        if not topics:
            return None

        return random.choice(topics)

    def end_conversation(self):
        if not self.flag:
            return
        # store in user topics the current topics of conversation
        topics_list = self.user_topics
        for topic in self.current_topics:
            if topic not in topics_list:
                topics_list += [topic,]

        if self.new:
            final = ""
            for t in topics_list:
                final += f"{t}\n"
            self.user_db.add(
                documents=[
                    final
                ],
                metadatas=[
                    {"type": "topics"}
                ],
                ids=[
                    str(datetime.now())
                ]
            )

        else:
            results = self.user_db.query(
                query_texts=[
                    "topic"
                ],
                n_results=1,
                where={"type": "topics"}
            )
            final = ""
            for t in topics_list:
                final += f"{t}\n"
            id = results['ids'][0][0]
            self.user_db.update(
                ids=[id],
                documents=final,
                metadatas=[{"type": "topics"}]
            )

        if self.debug:
            print(f"TOPIC MANAGER: Stored new user topics in db {topics_list}")
