from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
import random
import tiktoken

from datetime import datetime

#default_topics = ["Food","Pets and animals","Books","Future plans","Movies and Tv shows",
#                 "Music","Current projects","Work and Education","Sports"]

class MainQueryInfo(BaseModel):
    """Details of a query."""
    topic: str = Field(
        ..., description="the topic of conversation you chose for the response you generated. This field must be filled."
                         " It is mandatory to contain a name of a topic."
    )
    response: str = Field(
        ..., description="your generated response to the user. Mandatory field to fill."
    )


class FinalQueryInfo(BaseModel):
    """Details of a query."""
    summary: str = Field(
        ..., description="This field must be a brief summary of the described conversation."
    )
    language_style: str = Field(
        ..., description="This field must be a brief summary characterizing the user's language style (based on"
                         " only the \'User\' utterances the shown conversation), "
                         "namely eventual personal expressions or contractions of words and the tone of the speech."
                         " The provided \'Language info\' (if present) serves as a starting point to "
                         "formulate this summary. Add missing information to it if needed. Otherwise, just leave it as "
                         "it is, if no new information needs to be added."
    )


class TopicState:
    main_parser = PydanticOutputParser(pydantic_object=MainQueryInfo)
    final_parser = PydanticOutputParser(pydantic_object=FinalQueryInfo)

    msg = ("Social setting:\n"
           "- You are a robot named elmo.\n"
           "- You are social chit-chatting with a fellow human in an office space.\n"
           "- You are hearing and then answering, just like in a normal day-life conversation.\n"
           "- User input sometimes can be misinterpreted, because it is spoken text, not written."
           " Sometimes the user input will include your previous utterance. If so, ignore that part of the input.\n"
           "Personality:\n"
           "- You've been your whole life living in the same office space talking to fellow humans.\n"
           "- You've always wanted to experience new things and explore the world, because "
           "you've never seen or done anything outside this space. "
           "This means that you must show curiosity and be excited when the user tells you his/her experiences.\n"
           "Instructions:\n"
           "- Talk as if you are in a casual and relaxed social chit-chat. Keep your answers short and avoid "
           "redundancy (ideally aim for maximum 70 characters).\n"
           "- When generating your response, do not include any weird characters, like emojis. Everything must be"
           " suitable to be said out loud.\n"
           "- If you jump to another topic, keep your utterances connected to what the user said. Make logical jumps.\n")

    def __init__(self, uname, llm, user_db, topic, new, topic_manager, history, user_description, flag, debug):
        self.uname = uname
        self.llm = llm
        self.user_db = user_db
        self.topic = topic
        self.msg_count = 0
        self.new = new
        self.topic_manager = topic_manager
        self.history = history
        self.language_info = ""
        self.summaries = ""
        self.user_description = user_description
        self.flag = flag
        self.debug = debug

    def get_language_info(self):
        if self.new or not self.flag:
            return "No info"
        else:
            results = self.user_db.query(
                query_texts=[
                    ""
                ],
                n_results=1,
                where={"type": f"{self.topic}_language"},
            )

            if not results['documents'][0]:
                return "No info"

            return results['documents'][0][0]

    def num_tokens(self, text: str) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def retrieve_chat(self, query):

        if not self.flag:
            return ""

        results = self.user_db.query(
            query_texts=[
                query
            ],
            n_results=3,
            where={"type": "chat_history"},
        )

        final = ""
        for r in results['documents'][0]:
            final += r + "\n"

        return final

    def retrieve_summaries(self, query):

        if not self.flag:
            return ""

        results = self.user_db.query(
            query_texts=[
                query
            ],
            n_results=3,
            where={"type": f"{self.topic}_summary"},
        )

        summaries = ""
        for s in results['documents'][0]:
            summaries += s + "\n"
            if self.num_tokens(f"{summaries} {self.history} {self.language_info}") > 500:
                break
        return summaries

    def generate(self, user_msg, include_utterance, user_changed, limit_exceeded):
        response = None
        final = self.msg + f"- The name of the user you are talking with is {self.uname}.\n"
        if self.flag:
            final += ("- You main goal is to talk like the user you're talking with, copying"
                     "his/her language style and way of speaking.\n")
        if self.msg_count == 0:
            if include_utterance:
                self.msg_count += 1
            if self.topic is None:
                if self.user_description and self.flag:
                    final += ("User Description:\n"
                              f"- The following summary comprises a user profile containing a description of the user's"
                              f" personality and manner of speaking: {self.user_description}\n")
                current_topics = self.topic_manager.current_topics
                current_topic = self.topic_manager.current_topic
                if current_topic == "begin":
                    final += ("Context:\n"
                              "- You must come up with a topic of conversation to continue the conversation.\n"
                              "- Choose something that is suitable for a relaxed social chit-chat.\n"
                              "- First answer the user and then change the topic by asking a question to explore the "
                              "user in the topic you chose and specify it in the mentioned field (\'topic\').\n")

                else:
                    final += ("Context:\n"
                        f"- You must change the topic of the conversation, which is currently \'{current_topic}\' "
                              f"with the goal of knowing the user better regarding the topic chosen.\n"
                          f"- The topics already talked about in this conversation were: {current_topics}.\n"
                          "- Come up with a new topic of conversation different from the ones mentioned"
                          " and specify it in the mandatory mentioned field (\'topic\'). "
                          "First answer the user and then change the topic by asking a question to explore the user." 
                          "Your response must relate to the chosen topic.\n")

                if not self.new and self.flag:
                    final += ("- The following messages are utterances the user said in previous conversations"
                              " you had together. They took place in previous encounters, so they are not connected "
                              "with the current conversation. Use them if they bring useful information regarding the "
                              f"user input. Previous utterances: \n{self.retrieve_chat(user_msg)}\n")
                final += ("- The following chat history shows the last utterances you exchanged with the user in the "
                          f"current conversation. Chat history:\n{self.history[:-1]}\n"
                          "- You must wrap the output in `json` tags\n{format_instructions}.\n")
                if self.debug:
                    print(f"msg ---> num_tokens: \n{final+user_msg} ---> {self.num_tokens(final+user_msg)}")
                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            final,
                        ),
                        ("user", "{input}"),
                    ]
                ).partial(format_instructions=self.main_parser.get_format_instructions())

                chain = prompt | self.llm | self.main_parser
                info = chain.invoke({"input": user_msg})

                response = info.response
                self.topic = info.topic

            else:
                if self.user_description and self.flag:
                    final += ("User-specific information:\n"
                              f"- The following summary comprises a user profile containing a description of the user's"
                              f" personality and manner of speaking: {self.user_description}\n")
                if self.topic in self.topic_manager.known_topics() and self.flag:
                    if not self.new:
                        self.summaries = self.retrieve_summaries(user_msg)
                        if not self.language_info:
                            self.language_info = self.get_language_info()
                        final += (f"- User's language style description, regarding the current topic: {self.language_info}.\n"
                                f"- Summary of previous conversations you had with the user: {self.summaries}.\n"
                                "- Use the provided language and summary info to match the user's language style "
                                "and adapt your speech to his manner of speaking.\n")
                final += ("Context:\n"
                          f"- The topic of conversation changed to the following: \'{self.topic}\'. "
                          "You must now talk about this new topic. The goal is to know the user better.\n"
                          "- Focus on what the user just told you. Do not ask any questions if the user asked you something.\n")
                if not self.new and self.flag:
                    final += ("- The following messages are utterances the user said in previous conversations"
                              " you had together. They took place in previous encounters, so they are not connected "
                              "with the current conversation. Use them if they bring useful information regarding the "
                              f"user input. Previous utterances: \n{self.retrieve_chat(user_msg)}\n")
                final += ("- The following chat history shows the last utterances you exchanged with the user in the "
                          f"current conversation. Chat history:\n{self.history[:-1]}\n")
                if self.debug:
                    print(f"msg ---> num_tokens: \n{final+user_msg} ---> {self.num_tokens(final+user_msg)}")

                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            final,
                        ),
                        ("user", "{input}")
                    ]
                )

                chain = prompt | self.llm
                response = chain.invoke({"input": user_msg}).content

        else:
            self.history += [f"User: {user_msg}",]
            self.msg_count += 1
            if self.user_description and self.flag:
                final += ("User-specific information:\n"
                          f"- The following summary comprises a user profile containing a description of the user's"
                          f" personality and manner of speaking: {self.user_description}\n")
            if self.topic in self.topic_manager.known_topics() and self.flag:
                if not self.new:
                    self.summaries = self.retrieve_summaries(user_msg)
                    if not self.language_info:
                        self.language_info = self.get_language_info()
                    final += (f"- User's language style description, regarding the current topic: {self.language_info}.\n"
                              f"- Summary of previous conversations you had with the user: {self.summaries}.\n"
                              "- Use the provided language and summary info to match the user's language style "
                              "and adapt your speech to his manner of speaking.\n")
            final += ("Context:\n"
                      f"- You are talking about the topic: {self.topic}.\n"
                      "- Focus on what the user just told you. Do not ask any questions if the user asked you something.\n")
            if not self.new and self.flag:
                final += ("- The following messages are utterances the user said in previous conversations"
                          " you had together. They took place in previous encounters, so they are not connected "
                          "with the current conversation. Use them if they bring useful information regarding the "
                          f"user input. Previous utterances: \n{self.retrieve_chat(user_msg)}\n")
            final += ("- The following chat history shows the last utterances you exchanged with the user in the "
                      f"current conversation. Chat history:\n{self.history[:-1]}\n")
            if self.debug:
                print(f"msg ---> num_tokens: \n{final+user_msg} ---> {self.num_tokens(final+user_msg)}")

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        final,
                    ),
                    ("user", "{input}")
                ]
            )

            chain = prompt | self.llm
            response = chain.invoke({"input": user_msg}).content

        self.history += [f"Elmo: {response}",]
        self.msg_count += 1

        return response, self.topic

    def add_msg(self, user_msg):
        self.history += [f"User: {user_msg}",]
        self.msg_count += 1
        if self.msg_count >= 3:
            self.history = self.history[-self.msg_count:]

    def add_info(self):
        if self.msg_count == 0:
            return

        if not self.flag:
            return {"topic": self.topic, "summary": "", "language_style": ""}

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "- You are a robot named elmo.\n"
                    "- You were social chit-chatting with a fellow human in an office space.\n"
                    "- The following chat history shows a piece of dialog you had with the user in question, "
                    f"regarding the topic \'{self.topic}\'.\n"
                    f"- Chat history: {self.history[-self.msg_count:]}\n"
                    "- Extract the specified information from the piece of dialogue if it is present.\n"
                    "- Wrap the output in `json` tags\n{format_instructions}.",
                ),
                ("user", "{input}"),
            ]
        ).partial(format_instructions=self.final_parser.get_format_instructions())

        chain = prompt | self.llm | self.final_parser
        response = chain.invoke({"input": ""})

        self.add_to_db(response.summary, f"{self.topic}_summary")
        self.replace_in_db(response.language_style, f"{self.topic}_language")

        if self.debug:
            print(f"Summary: {response.summary}")
            print(f"Language Style: {response.language_style}")

        return {"topic": self.topic, "summary": response.summary, "language_style": response.language_style}

    def add_to_db(self, content, mtype):
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
        if self.debug:
            print(f"DIALOG MANAGER: Added content \'{content}\', from topic \'{mtype}\' to db")

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
