import json
import os
from datetime import datetime

for filename in ("../users_memory.txt", "../users_no_memory.txt"):
    with open(filename, "r") as f:
        listing = f.read()
        users = listing.split()
        print(filename)
        for uid in users:
            directory = f"../logs/{uid}"
            with open(f"../first_names/{uid}.txt", "r") as ff:
                user_name = ff.read()
                print(f"Details for \'{user_name}\' ({uid}):\n")

            n_turns_all = 0
            total_time_all = 0
            total_elapsed_time = 0
            n_interactions = 0
            n_topics_changed = 0
            n_total_topics = 0
            total_avg_resp_time = 0
            user_ended = 0
            for filename in os.listdir(directory):
                f = os.path.join(directory, filename)
                # checking if it is a file
                with open(f, 'r') as jsonfile:
                    n_interactions += 1
                    data = json.load(jsonfile)
                    if data["user_ended"]:
                        user_ended += 1
                    user_changed = []
                    topic_limit = []

                    i = 0
                    n_turns = 0
                    total_time = 0
                    chat = ""
                    for turn in data["conversation"]:
                        if turn["user_changed"]:
                            user_changed += [prev_topic,]
                        if turn["topic_limit"]:
                            topic_limit += [turn["topic"],]
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
                        prev_topic = turn["topic"]

                    avg_resp_time = total_time / n_turns
                    total_time_all += total_time

                    topics = []
                    for topic in data["topics"]:
                        topics += [topic["topic"],]

                n_topics_changed += len(user_changed)
                n_total_topics += len(topics)

                print(f"Interaction {n_interactions}:\n")
                #print(f"User profile: {user_profile}\n")
                #print(f"Conversation:\n{chat}\n")
                #print(f"Topics (summary and language style):\n\n{topic_details}")
                #print(f"Final summary: {final_summary}\n")
                print(f"Topics talked about: {topics}")
                print(f"Topics changed by the user: {user_changed}\n")
                print(f"Limit exceeded topics: {topic_limit}\n")
                #print(f"User ended the conversation?: {user_ended}\n\n")
                print(f"Average response time for this interaction: {avg_resp_time} seconds\n")
                #print(f"Total time of interaction: {elapsed_time} seconds ({elapsed_time//60} minutes and {elapsed_time - ((elapsed_time//60)*60)} seconds)\n\n")

                total_avg_resp_time = total_time_all / n_turns_all

            print(f"Percentage of ended interactions: {user_ended} / {n_interactions} = {user_ended/n_interactions}")
            print(f"Final total topics changed vs total topics: {n_topics_changed} vs {n_total_topics} = {n_topics_changed/n_total_topics}")
            print(f"Total average response time for all {n_interactions} interactions: {total_avg_resp_time} seconds\n")
            #print(f"Total time of all {n_interactions} interactions: {total_elapsed_time} seconds ({total_elapsed_time//60} minutes and {total_elapsed_time - ((total_elapsed_time//60)*60)} seconds)\n")

            input("\n\nNext User\n")


