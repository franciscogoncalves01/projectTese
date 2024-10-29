from scipy.stats import shapiro

# Assuming these are your data for each group
memory_group_ended_interactions = [0.625,0.25,0.25,0,0.25,0]  # Memory group data
no_memory_group_ended_interactions = [0.8,0.6,0.6,0.5,0.25,0.6]  # No-memory group data

memory_group_average_response_times = [2.81,3.44,3.4,5.18,3.56,6.44]  # Memory group data
no_memory_group_average_response_times = [2.54,3.26,3.77,3.22,3.6,3.278]  # No-memory group data

memory_group_changed_topic = [0.208,0.167,0.182,0.1,0.583,0.091]  # Memory group data
no_memory_changed_topic = [0.769,0.091,0.231,0.2,0.2,0.3]  # No-memory group data

print("-----Ended interactions-----")
# Perform the Shapiro-Wilk test for the memory group
stat_memory, p_value_memory = shapiro(memory_group_ended_interactions)
print(f'Memory Group - Statistic: {stat_memory}, P-value: {p_value_memory}')

# Perform the Shapiro-Wilk test for the no-memory group
stat_no_memory, p_value_no_memory = shapiro(no_memory_group_ended_interactions)
print(f'No Memory Group - Statistic: {stat_no_memory}, P-value: {p_value_no_memory}')

print("-----Average Response Times-----")
# Perform the Shapiro-Wilk test for the memory group
stat_memory, p_value_memory = shapiro(memory_group_average_response_times)
print(f'Memory Group - Statistic: {stat_memory}, P-value: {p_value_memory}')

# Perform the Shapiro-Wilk test for the no-memory group
stat_no_memory, p_value_no_memory = shapiro(no_memory_group_average_response_times)
print(f'No Memory Group - Statistic: {stat_no_memory}, P-value: {p_value_no_memory}')

print("-----Changed Topics-----")
# Perform the Shapiro-Wilk test for the memory group
stat_memory, p_value_memory = shapiro(memory_group_changed_topic)
print(f'Memory Group - Statistic: {stat_memory}, P-value: {p_value_memory}')

# Perform the Shapiro-Wilk test for the no-memory group
stat_no_memory, p_value_no_memory = shapiro(no_memory_changed_topic)
print(f'No Memory Group - Statistic: {stat_no_memory}, P-value: {p_value_no_memory}')
