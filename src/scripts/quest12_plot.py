import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

m_elmo_knows = [2,3,4,3,2,4]
no_m_elmo_knows = [1,2,4,3,2,2]

m_topic_transition = [2,3,2,3,3,3]
no_m_topic_transition = [2,3,2,4,4,4]

topic_transition_data = pd.DataFrame({
    'User Evaluation Score': m_topic_transition + no_m_topic_transition,
    'Group': ['Memory'] * len(m_topic_transition) + ['No Memory'] * len(no_m_topic_transition)
})

# Create a box plot for Ended Interactions
plt.figure(figsize=(8, 6))
sns.boxplot(x='Group', y='User Evaluation Score', data=topic_transition_data, palette="coolwarm")  # Different color palette
plt.show()
