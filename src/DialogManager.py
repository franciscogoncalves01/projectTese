from TopicManager import TopicManager
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator

from datetime import datetime
from GreetingState import GreetingState
from TopicState import TopicState
import json
from pathlib import Path

class EvalQueryInfo(BaseModel):
    """Details of a query."""

    ending: str = Field(
        ..., description="If the user intends to end the conversation (if an expression of closure is being "
                         "said by the user, like \'goodbye\', \'see you later\', \'gotta go\', or equivalent ones). "
                         "Must be one of the two: {\'yes\' or \'no\'}. \'Thank you Elmo\' is not an ending sentence."
    )
    user_changed: str = Field(
        ..., description="- if the user changed to a different topic, the field is the name of that topic "
                         "(look for it in the given list of user topics). If the conversation just started, "
                         "check if the user takes initiative on choosing a topic of conversation, meaning that he/she"
                         " does not just greet you and attempts to lead the conversation. The topic chosen"
                         " must be something generic and not very specific.\n"
                         "- If the user only asked to change the topic, meaning that no specific topic can be retrieved"
                         " from his response, the field must be \'yes\'.\n"
                         "- If the conversation did not change topic, the field must be \'no\'."
    )
    question: str = Field(
        ..., description="- if the user made a question (statement ending with question mark) or asked for your advice/"
                         "recommendation on something, this field must be \'yes\'.\n"
                         "- If the user did not ask for any information, the field must be \'no\'."
    )
    """maintain_topic: str = Field(
        ..., description="- If the user asked a question or showed enthusiasm, meaning that he is interested with this"
                         "topic of conversation, this field must be \'yes\'."
                         "- If the user answered with a one-word sentence, evaluate if he is not interested in the"
                         " current topic of conversation, and if so, this field must be \'no\'.\n"

    )"""

class DialogManager:

    eval_parser = PydanticOutputParser(pydantic_object=EvalQueryInfo)
    # Prompt
    eval_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Extract the specified information from the piece of dialogue if it is present,"
                "Wrap the output in `json` tags\n{format_instructions}."
                "The given chat history is the last few messages that Elmo robot exchanged with the user."
                "Focus on the last message of the user. You must evaluate it regarding the specified fields."
                "Topics Elmo talked about with the user: {user_topics}"
                "Current topic and chat history: {topic_history}",
            ),
            ("user", "{input}"),
        ]
    ).partial(format_instructions=eval_parser.get_format_instructions())

    def __init__(self, user_id, uname, llm, llm_eval, user_db, new, flag, debug):
        self.flag = flag
        self.user_id = user_id
        self.uname = uname
        self.llm = llm
        self.llm_eval = llm_eval
        self.user_db = user_db
        self.new = new
        self.topic_manager = TopicManager(user_db, new, flag, debug)
        self.history = []
        self.chat = []
        self.msg_count = 0 # msg count for current_topic
        self.current_topic = "begin"
        self.current_topics = []
        self.start_time = datetime.now()
        self.end = False
        self.user_description = self.get_user_description()
        self.states = [GreetingState(self.uname, llm, user_db, new, self.user_description, flag),]
        self.eval_chain = self.eval_prompt | self.llm_eval | self.eval_parser
        self.change_topic = False
        self.limit_exceeded = False
        self.user_changed = False
        self.debug = debug
        self.ext_code = False

    def get_user_description(self):

        if self.new or not self.flag:
            return ""

        results = self.user_db.query(
            query_texts=[
                ""
            ],
            n_results=1,
            where={"type": "user_description"},
        )

        if not results['documents'][0]:
            return ""

        return results['documents'][0][0]

    def add_state(self, topic):
        self.states += [TopicState(self.uname, self.llm, self.user_db, topic,
                                   self.new, self.topic_manager, self.chat[-4:],
                                   self.user_description, self.flag, self.debug),]

    def run(self, user_msg, user_choice):

        response = None

        current_time = datetime.now()

        if self.current_topic == "begin":
            topic = self.topic_manager.choose_topic()
            self.add_state(topic)
            response, topic = self.states[-1].generate(user_msg, False, False, False)
            self.current_topic = topic
            self.topic_manager.add_topic(topic)
            self.msg_count = 1
            self.change_topic = False

        elif (current_time - self.start_time).total_seconds() >= 240: # 4 mins have passed
            self.end = True
            self.states[-1].add_msg(user_msg)
            response = self.ending_message(user_msg)
            return response

        elif user_choice is not None:
            self.add_state(user_choice)
            self.current_topic = user_choice
            self.topic_manager.add_topic(user_choice)
            response, topic = self.states[-1].generate(user_msg, True, True, False)
            self.msg_count = 2

        elif self.change_topic:
            self.states[-1].add_msg(user_msg)
            topic = self.topic_manager.choose_topic()
            self.add_state(topic)
            response, topic = self.states[-1].generate(user_msg, False, False, self.limit_exceeded)
            self.current_topic = topic
            self.topic_manager.add_topic(topic)
            self.msg_count = 1
            self.change_topic = False

        else:
            response, topic = self.states[-1].generate(user_msg, True, False, False)
            self.msg_count += 1

        self.limit_exceeded = False

        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S-%f")
        self.history += [{"timestamp": formatted_datetime, "message": f"Elmo: {response}", "topic": self.current_topic,
                          "user_changed": self.user_changed, "topic_limit": self.limit_exceeded},]
        self.chat += [f"Elmo: {response}",]

        self.user_changed = False

        return response

    def greeting_message(self):
        greeting = self.states[0].generate("", "", False, False)
        self.msg_count += 1
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S-%f")
        self.history += [{"timestamp": formatted_datetime, "message": f"Elmo: {greeting}","topic": "greeting",
                          "user_changed": False, "topic_limit": False},]
        self.chat += [f"Elmo: {greeting}",]
        return greeting

    def ending_message(self, user_msg):

        endings = None

        if self.flag:
            results = self.user_db.query(
                query_texts=[
                    "ending"
                ],
                n_results=1,
                where={"type": "ending"}
            )
            if results['documents'][0]:
                endings = results['documents'][0][0]

        if self.end:
            if self.new or endings is None:
                msg = ("You are a robot named elmo. You are ending a conversation with your partner. "
                       "When generating your response, do not include any weird characters, like emojis. Everything must be"
                       " suitable to be said out loud."
                       f"The user name is {self.uname}. "
                       "If the user made you a question, answer him. After that, say that you need to gather the data"
                       " and you hope to see him/her soon."
                       " Do not ask him anything. The provided chat history includes the last few dialog messages from your conversation with the user."
                       f"Chat history: {self.chat[-self.msg_count:-1]} ")
            else:
                msg = ("You are a robot named elmo. You are ending a conversation with your partner. "
                       "When generating your response, do not include any weird characters, like emojis. Everything must be"
                       " suitable to be said out loud."
                       f"The user name is {self.uname}. "
                       "If the user made you a question, answer him. After that, say that you need to gather the data."
                       f"Try to use one of these endings used by the user previously. Previous endings: {endings}. "
                       " Do not ask him anything. The provided chat history includes the last few dialog messages from your conversation with the user."
                       f"Chat history: {self.chat[-self.msg_count:-1]} ")
        else:
            if self.new or endings is None:
                msg = ("You are a robot named elmo. Your partner intends to end the conversation. "
                       "When generating your response, do not include any weird characters, like emojis. Everything must be"
                       " suitable to be said out loud."
                       f"The user name is {self.uname}. "
                       "Say goodbye in a nice way and state that you hope to see him soon. Do not ask him anything."
                       "The provided chat history includes the last few dialog messages from your conversation with the user."
                       f"Chat history: {self.chat[-self.msg_count:-1]} ")
            else:
                msg = ("You are a robot named elmo. Your partner intends to end the conversation. "
                       "When generating your response, do not include any weird characters, like emojis. Everything must be"
                       " suitable to be said out loud."
                       f"The user name is {self.uname}. "
                       "Try to use one of these endings used by the user previously, but do not repeat the one"
                       f" the user is saying to you. Previous endings: {endings}."
                       " Do not ask him anything. The provided chat history includes the last few dialog messages from your conversation with the user."
                       f"Chat history: {self.chat[-self.msg_count:-1]} ")

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

        ending = chain.invoke({"input": user_msg})
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S-%f")
        self.history += [{"timestamp": formatted_datetime, "message": f"Elmo: {ending.content}","topic": "ending",
                          "user_changed": False, "topic_limit": False},]
        self.chat += [f"Elmo: {ending.content}",]

        self.ext_code = True
        self.topic_manager.end_conversation()

        return ending.content

    def eval(self, user_msg):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S-%f")

        topics = self.topic_manager.known_topics()

        info = self.eval_chain.invoke({"user_topics": f"{topics}",
                                  "topic_history": f"{self.current_topic}; History: {self.chat}", "input": user_msg})

        if self.debug:
            print(info)
        self.msg_count += 1

        if self.current_topic == "begin":
            if info.user_changed != "no" and info.user_changed != "yes": # user decided topic in the beginning
                self.history += [{"timestamp": formatted_datetime, "message": f"User: {user_msg}", "topic": "greeting",
                                  "user_changed": True, "topic_limit": False},]
                self.chat += [f"User: {user_msg}",]
                return self.run(user_msg, info.user_changed), self.ext_code
            if self.flag:
                self.add_greeting(user_msg)
            self.history += [{"timestamp": formatted_datetime, "message": f"User: {user_msg}", "topic": "greeting",
                              "user_changed": False, "topic_limit": False},]
            self.chat += [f"User: {user_msg}",]
            self.msg_count = 0
            self.change_topic = True
            return self.run(user_msg, None), self.ext_code

        if info.ending == "yes": # if the user intends to end the conversation
            self.history += [{"timestamp": formatted_datetime, "message": f"User: {user_msg}","topic": "ending",
                              "user_changed": False, "topic_limit": False},]
            self.chat += [f"User: {user_msg}",]
            if self.flag:
                self.add_ending(user_msg)
            return self.ending_message(user_msg), self.ext_code
        elif info.user_changed == "no": # user did not change topic
            if self.msg_count >= 8: # limit exceeded
                if info.question == "no":
                    self.change_topic = True
                    self.limit_exceeded = True
            self.history += [{"timestamp": formatted_datetime, "message": f"User: {user_msg}",
                              "topic": self.current_topic, "user_changed": self.user_changed,
                              "topic_limit": self.limit_exceeded},]
            self.chat += [f"User: {user_msg}",]
            return self.run(user_msg, None), self.ext_code

        elif info.user_changed == "yes": # user asked to change topic
            self.history += [{"timestamp": formatted_datetime, "message": f"User: {user_msg}",
                              "topic": self.current_topic, "user_changed": self.user_changed,
                              "topic_limit": self.limit_exceeded},]
            self.chat += [f"User: {user_msg}",]
            self.user_changed = True
            self.change_topic = True
            return self.run(user_msg, None), self.ext_code
        else:
            if info.user_changed == self.current_topic: # user did not change topic (llm mislead)
                self.history += [{"timestamp": formatted_datetime, "message": f"User: {user_msg}",
                                  "topic": self.current_topic, "user_changed": self.user_changed,
                                  "topic_limit": self.limit_exceeded},]
                self.chat += [f"User: {user_msg}",]
                return self.run(user_msg, None), self.ext_code
            self.user_changed = True
            self.history += [{"timestamp": formatted_datetime, "message": f"User: {user_msg}",
                              "topic": info.user_changed, "user_changed": self.user_changed,
                              "topic_limit": self.limit_exceeded},]
            self.chat += [f"User: {user_msg}",]
            return self.run(user_msg, info.user_changed), self.ext_code # user changed topic

    def add_chat_to_db(self):
        length = len(self.chat)

        for i in range(0, length-1, 2):
            self.user_db.add(
                documents=[
                    f"{self.chat[i]}; {self.chat[i+1]}"
                ],
                metadatas=[
                    {"type": "chat_history"}
                ],
                ids=[
                    str(datetime.now())
                ]
            )


    def add_ending(self, msg):
        results = self.user_db.query(
            query_texts=[
                "ending"
            ],
            n_results=1,
            where={"type": "ending"}
        )
        if not results['documents'][0]:
            self.user_db.add(
                documents=[
                    f"User: {msg}"
                ],
                metadatas=[
                    {"type": "ending"}
                ],
                ids=[
                    str(datetime.now())
                ]
            )
        else:
            id = results['ids'][0][0]
            endings = f"{results['documents'][0][0]}\n{msg}"
            self.user_db.update(
                ids=[id],
                documents=[endings],
                metadatas=[{"type": "ending"}]
            )
        if self.debug:
            print(f"DIALOG MANAGER: Added ending message \'{msg}\' to db")

    def add_greeting(self, msg):
        results = self.user_db.query(
            query_texts=[
                "greeting"
            ],
            n_results=1,
            where={"type": "greeting"}
        )

        if not results['documents'][0]:
            self.user_db.add(
                documents=[
                    f"User: {msg}"
                ],
                metadatas=[
                    {"type": "greeting"}
                ],
                ids=[
                    str(datetime.now())
                ]
            )
        else:
            rid = results['ids'][0][0]
            greetings = f"{results['documents'][0][0]}\n{msg}"
            self.user_db.update(
                ids=[rid],
                documents=[greetings],
                metadatas=[{"type": "greeting"}]
            )

    def generate_user_info(self):
        for state in self.states[1:]:
            self.current_topics += [state.add_info(),]

        if not self.flag:
            self.write_to_json("")
            return

        msg = ("- You are a robot named elmo.\n"
                "- You were social chit-chatting with a fellow human in an office space.\n"
                "- The following chat history shows the dialog you just had with the user in question.\n"
                f"- Chat history: {self.chat}\n"
                "- Elaborate a user profile describing the user's personality, tastes and manner of speaking, based on the "
               "above chat history.")

        if self.user_description:
            msg += (" Use the following summary as a starting point and add missing information if needed. Just keep "
                    "the crucial information to describe the user's personality, the resulting description must not"
                    " exceed 1000 characters. Alter information if needed to stay within the limit range. "
                    f"User description: {self.user_description}")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    msg,
                ),
                ("user", "{input}")
            ]
        )

        chain = prompt | self.llm_eval
        response = chain.invoke({"input": ""}).content

        self.replace_in_db(response, "user_description")
        self.write_to_json(response)
        self.add_chat_to_db()

    def write_to_json(self, final_summary):
        if self.end:
            user_ended = False
        else:
            user_ended = True

        final_dict = {
            "user_profile": self.user_description,
            "conversation": self.history,
            "topics": self.current_topics,
            "final_summary": final_summary,
            "user_ended": user_ended
        }

        Path(f"logs/{self.user_id}").mkdir(exist_ok=True)
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

        with open(f"logs/{self.user_id}/session_{formatted_datetime}.json", "w") as outfile:
            json.dump(final_dict, outfile)

    def replace_in_db(self, content, mtype):
        results = self.user_db.query(
            query_texts=[
                ""
            ],
            n_results=1,
            where={"type": mtype}
        )

        if not results['documents'][0]:
            self.user_db.add(
                documents=[
                    content
                ],
                metadatas=[
                    {"type": mtype}
                ],
                ids=[
                    str(datetime.now())
                ]
            )
        else:
            rid = results['ids'][0][0]
            self.user_db.update(
                ids=[rid],
                documents=[content],
                metadatas=[{"type": mtype}]
            )
