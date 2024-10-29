import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

memory_group_changed_topic = [0.208,0.125,0.083,0.154,0.563,0.083]  # Memory group data
no_memory_changed_topic = [0.769,0.091,0.231,0.2,0.2,0.3]  # No-memory group data

# Combine data into DataFrames for Seaborn
changed_topic_data = pd.DataFrame({
    'Changed Topic Ratio': memory_group_changed_topic + no_memory_changed_topic,
    'Group': ['Memory'] * len(memory_group_changed_topic) + ['No Memory'] * len(no_memory_changed_topic)
})

# Create a box plot for Changed Topics
plt.figure(figsize=(8, 6))
sns.boxplot(x='Group', y='Changed Topic Ratio', data=changed_topic_data, palette="coolwarm")  # Color palette can be changed
plt.ylim(0, 0.5)
plt.show()
