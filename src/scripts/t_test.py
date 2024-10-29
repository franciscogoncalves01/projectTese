from scipy.stats import ttest_ind, levene, mannwhitneyu
import numpy as np
import math

# Assuming these are your data for each group
memory_group_ended_interactions = np.array([0.625,0.25,0.25,0,0.25,0])  # Memory group data
no_memory_group_ended_interactions = np.array([0.8,0.6,0.6,0.5,0.25,0.6])  # No-memory group data

memory_group_average_response_times = [2.81,3.44,3.4,5.18,3.56,6.44]  # Memory group data
no_memory_group_average_response_times = [2.54,3.26,3.77,3.22,3.6,3.278]  # No-memory group data

memory_group_language_style = [2,5,5,4,4,5]
no_memory_group_language_style = [3,3,4,4,5,3]

memory_group_response_time_acc = np.array([3,4,1,3,4,5])
no_memory_group_response_time_acc = np.array([2,2,3,4,4,4])

mem_var, nomem_var = np.var(memory_group_response_time_acc), np.var(no_memory_group_response_time_acc)
print(f"Memory mean and standard deviation: {np.mean(memory_group_response_time_acc)} ; {math.sqrt(mem_var)}")
print(f"No memory mean and standard deviation: {np.mean(no_memory_group_response_time_acc)} ; {math.sqrt(nomem_var)}")

# Perform independent t-test
#t_stat, p_value = ttest_ind(memory_group_average_response_times,no_memory_group_average_response_times, equal_var=True)  # Set equal_var to True or False based on Levene's test
#print(f'T-statistic: {t_stat}, P-value: {p_value}')
u_stat, p_value = mannwhitneyu(memory_group_response_time_acc,no_memory_group_response_time_acc, alternative='two-sided')
print(f'U-statistic: {u_stat}, P-value: {p_value}')
"""
stat, p = levene(memory_group_average_response_times, no_memory_group_average_response_times)
print(p)

# Perform independent t-test
t_stat, p_value = ttest_ind(memory_group_average_response_times, no_memory_group_average_response_times, equal_var=p>0.05)  # Set equal_var to True or False based on Levene's test

print(f'Average Response Times:\nT-statistic: {t_stat}, P-value: {p_value}')

"""