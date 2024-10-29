import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

m_warmth = [1.5,3.33,3.67,3.5,3.33,3.67]
no_m_warmth = [3.17,3,2.5,1.83,3.5,3.17]

m_competence = [2.17,3.83,4.17,3.33,3.17,4.67]
no_m_competence = [3.33,2.67,3.17,3.33,3.83,4]

m_discomfort = [2.5,1.17,1.17,1,1.5,1.33]
no_m_discomfort = [1.83,1.83,2.5,1.83,1.33,1.5]

discomfort_data = pd.DataFrame({
    'Discomfort Score': m_discomfort + no_m_discomfort,
    'Group': ['Memory'] * len(m_discomfort) + ['No Memory'] * len(no_m_discomfort)
})

# Create a box plot for Ended Interactions
plt.figure(figsize=(8, 6))
sns.boxplot(x='Group', y='Discomfort Score', data=discomfort_data, palette="coolwarm")  # Different color palette
plt.show()
