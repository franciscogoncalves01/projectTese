from scipy.stats import mannwhitneyu
import math
import numpy as np

# Example data: ratios of topic changes for memory and no-memory groups
memory_group_changed_topic = [0.208,0.167,0.182,0.1,0.583,0.091]  # Memory group data
no_memory_changed_topic = [0.769,0.091,0.231,0.2,0.2,0.3]  # No-memory group data
"""
memory_group_response_time_acc = [3,4,1,3,4,5]
no_memory_group_response_time_acc = [2,2,3,4,4,4]

memory_group_language_style = [2,5,5,4,4,5]
no_memory_group_language_style = [3,3,4,4,5,3]
"""
# Perform the Mann-Whitney U test
mem_var, nomem_var = np.var(memory_group_changed_topic), np.var(no_memory_changed_topic)
print("Topic changing")
print(f"Memory mean and standard deviation: {np.mean(memory_group_changed_topic)} ; {math.sqrt(mem_var)}")
print(f"No memory mean and standard deviation: {np.mean(no_memory_changed_topic)} ; {math.sqrt(nomem_var)}")
stat, p_value = mannwhitneyu(memory_group_changed_topic, no_memory_changed_topic, alternative='two-sided')
print(f'U: {stat}, p: {p_value}')
"""
stat, p_value = mannwhitneyu(memory_group_response_time_acc, no_memory_group_response_time_acc, alternative='two-sided')
print(f'User acceptance to response time:\nStatistic: {stat}, P-value: {p_value}')

stat, p_value = mannwhitneyu(memory_group_language_style, no_memory_group_language_style, alternative='two-sided')
print(f'Language Style:\nStatistic: {stat}, P-value: {p_value}')
m_warmth = [1.5,3.33,3.67,3.5,3.33,3.67]
no_m_warmth = [3.17,3,2.5,1.83,3.5,3.17]

m_competence = [2.17,3.83,4.17,3.33,3.17,4.67]
no_m_competence = [3.33,2.67,3.17,3.33,3.83,4]

m_discomfort = [2.5,1.17,1.17,1,1.5,1.33]
no_m_discomfort = [1.83,1.83,2.5,1.83,1.33,1.5]

mem_var, nomem_var = np.var(m_warmth), np.var(no_m_warmth)
print("WARMTH")
print(f"Memory mean and standard deviation: {np.mean(m_warmth)} ; {math.sqrt(mem_var)}")
print(f"No memory mean and standard deviation: {np.mean(no_m_warmth)} ; {math.sqrt(nomem_var)}")
stat, p_value = mannwhitneyu(m_warmth, no_m_warmth, alternative='two-sided')
print(f'Statistic: {stat}, P-value: {p_value}')

mem_var, nomem_var = np.var(m_competence), np.var(no_m_competence)
print("COMPETENCE")
print(f"Memory mean and standard deviation: {np.mean(m_competence)} ; {math.sqrt(mem_var)}")
print(f"No memory mean and standard deviation: {np.mean(no_m_competence)} ; {math.sqrt(nomem_var)}")
stat, p_value = mannwhitneyu(m_competence, no_m_competence, alternative='two-sided')
print(f'Statistic: {stat}, P-value: {p_value}')

mem_var, nomem_var = np.var(m_discomfort), np.var(no_m_discomfort)
print("DISCOMFORT")
print(f"Memory mean and standard deviation: {np.mean(m_discomfort)} ; {math.sqrt(mem_var)}")
print(f"No memory mean and standard deviation: {np.mean(no_m_discomfort)} ; {math.sqrt(nomem_var)}")
stat, p_value = mannwhitneyu(m_discomfort, no_m_discomfort, alternative='two-sided')
print(f'Statistic: {stat}, P-value: {p_value}')

m_elmo_knows = [2,3,4,3,2,4]
no_m_elmo_knows = [1,2,4,3,2,2]

m_topic_transition = [2,3,2,3,3,3]
no_m_topic_transition = [2,3,2,4,4,4]

mem_var, nomem_var = np.var(m_elmo_knows), np.var(no_m_elmo_knows)
print("Elmo knows")
print(f"Memory mean and standard deviation: {np.mean(m_elmo_knows)} ; {math.sqrt(mem_var)}")
print(f"No memory mean and standard deviation: {np.mean(no_m_elmo_knows)} ; {math.sqrt(nomem_var)}")
stat, p_value = mannwhitneyu(m_elmo_knows, no_m_elmo_knows, alternative='two-sided')
print(f'U: {stat}, p: {p_value}')

mem_var, nomem_var = np.var(m_topic_transition), np.var(no_m_topic_transition)
print("Topic transition")
print(f"Memory mean and standard deviation: {np.mean(m_topic_transition)} ; {math.sqrt(mem_var)}")
print(f"No memory mean and standard deviation: {np.mean(no_m_topic_transition)} ; {math.sqrt(nomem_var)}")
stat, p_value = mannwhitneyu(m_topic_transition, no_m_topic_transition, alternative='two-sided')
print(f'U: {stat}, p: {p_value}')

speech_recognizer = [3,4,4,4,3,4, 2,2,4,5,4,4]
speech_generator = [4,5,5,4,3,5, 4,4,3,4,5,3]
elmo_voice = [4,5,5,4,4,5, 4,4,3,4,5,4]

var = np.var(speech_recognizer)
print("Speech Recognizer")
print(f"Memory mean and standard deviation: {np.mean(speech_recognizer)} ; {math.sqrt(var)}")

var = np.var(speech_generator)
print("Speech Generator")
print(f"Memory mean and standard deviation: {np.mean(speech_generator)} ; {math.sqrt(var)}")

var = np.var(elmo_voice)
print("Elmo Voice")
print(f"Memory mean and standard deviation: {np.mean(elmo_voice)} ; {math.sqrt(var)}")
"""