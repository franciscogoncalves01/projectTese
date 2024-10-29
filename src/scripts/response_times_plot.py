import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

memory_group_average_response_times = [2.81,3.44,3.4,5.18,3.56,6.44]  # Memory group data
no_memory_group_average_response_times = [2.54,3.26,3.77,3.22,3.6,3.278]  # No-memory group data

average_response_time_data = pd.DataFrame({
    'Average Response Time (s)': memory_group_average_response_times + no_memory_group_average_response_times,
    'Group': ['Memory'] * len(memory_group_average_response_times) + ['No Memory'] * len(no_memory_group_average_response_times)
})

plt.figure(figsize=(8, 6))
sns.boxplot(x='Group', y='Average Response Time (s)', data=average_response_time_data, palette="coolwarm")  # Different color palette
plt.show()
