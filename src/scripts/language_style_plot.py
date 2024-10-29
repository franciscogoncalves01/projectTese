import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

memory_group_language_style = [2,5,5,4,4,5]
no_memory_group_language_style = [3,3,4,4,5,3]

language_style_data = pd.DataFrame({
    'User evaluation of robot\'s language style': memory_group_language_style + no_memory_group_language_style,
    'Group': ['Memory'] * len(memory_group_language_style) + ['No Memory'] * len(no_memory_group_language_style)
})

plt.figure(figsize=(8, 6))
sns.boxplot(x='Group', y='User evaluation of robot\'s language style', data=language_style_data, palette="coolwarm")  # Different color palette
plt.show()
