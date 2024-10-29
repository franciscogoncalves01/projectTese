import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

memory_group_ended_interactions = [0.625,0.25,0.25,0,0.25,0]  # Memory group data
no_memory_group_ended_interactions = [0.8,0.6,0.6,0.5,0.25,0.6]  # No-memory group data

ended_interactions_data = pd.DataFrame({
    'Ended Interactions Ratio': memory_group_ended_interactions + no_memory_group_ended_interactions,
    'Group': ['Memory'] * len(memory_group_ended_interactions) + ['No Memory'] * len(no_memory_group_ended_interactions)
})

# Create a box plot for Ended Interactions
plt.figure(figsize=(8, 6))
sns.boxplot(x='Group', y='Ended Interactions Ratio', data=ended_interactions_data, palette="coolwarm")  # Different color palette
plt.show()
