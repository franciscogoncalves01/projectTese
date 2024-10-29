import json
import os
from datetime import datetime

uid = input("user_id?\n> ")
directory = f"../logs/{uid}"
first = True
n_turns_all = 0
total_time_all = 0
n_interactions = 0
total_elapsed_time = 0

with open(f"../first_names/{uid}.txt", "r") as f:
    user_name = f.read()
    print(f"Resume of interactions with \'{user_name}\' ({uid}):\n")

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    with open(f, 'r') as jsonfile:
        n_interactions += 1
        data = json.load(jsonfile)
        user_profile = data["user_profile"]
        final_summary = data["final_summary"]
        user_ended = data["user_ended"]
        user_changed = []
        topic_limit = []

        print(f"{data["conversation"][0]["timestamp"]} -> {data["conversation"][-1]["timestamp"]}")
        first_ts = datetime.strptime(data["conversation"][0]["timestamp"], "%Y-%m-%d_%H-%M-%S-%f")
        last_ts = datetime.strptime(data["conversation"][-1]["timestamp"], "%Y-%m-%d_%H-%M-%S-%f")
        elapsed_time = (last_ts - first_ts).total_seconds()
        total_elapsed_time += elapsed_time

        i = 0
        n_turns = 0
        total_time = 0
        chat = ""
        for turn in data["conversation"]:
            if turn["user_changed"]:
                user_changed += [turn["topic"],]
            if turn["topic_limit"]:
                topic_limit += [turn["topic"],]
            chat += turn["message"] + "\n"
            if i == 0:
                i += 1
                continue
            elif i % 2 == 0:
                n_turns += 1
                n_turns_all += 1
                elmo_ts = datetime.strptime(turn["timestamp"], "%Y-%m-%d_%H-%M-%S-%f")
                total_time += (elmo_ts - user_ts).total_seconds()
            else:
                user_ts = datetime.strptime(turn["timestamp"], "%Y-%m-%d_%H-%M-%S-%f")
            i += 1

        avg_resp_time = total_time / n_turns
        total_time_all += total_time

        topic_details = ""
        for topic in data["topics"]:
            topic_details += (f"{topic["topic"]}:\n"
                              f"\tSummary: {topic["summary"]}\n"
                              f"\tLanguage Style: {topic["language_style"]}\n\n")

    print(f"Details of {filename[:-6]} (interaction {n_interactions}):\n")
    #print(f"User profile: {user_profile}\n")
    #print(f"Conversation:\n{chat}\n")
    #print(f"Topics (summary and language style):\n\n{topic_details}")
    #print(f"Final summary: {final_summary}\n")
    print(f"Topics changed by the user: {user_changed}\n")
    print(f"Limit exceeded topics: {topic_limit}\n")
    #print(f"User ended the conversation?: {user_ended}\n\n")
    #print(f"Average response time for this interaction: {avg_resp_time} seconds\n")
    #print(f"Total time of interaction: {elapsed_time} seconds ({elapsed_time//60} minutes and {elapsed_time - ((elapsed_time//60)*60)} seconds)\n\n")

total_avg_resp_time = total_time_all / n_turns_all

#print(f"Total average response time for all {n_interactions} interactions: {total_avg_resp_time} seconds\n")
#print(f"Total time of all {n_interactions} interactions: {total_elapsed_time} seconds ({total_elapsed_time//60} minutes and {total_elapsed_time - ((total_elapsed_time//60)*60)} seconds)\n")

