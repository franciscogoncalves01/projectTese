import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

memory_group_response_time_acc = [3,4,1,3,4,5]
no_memory_group_response_time_acc = [2,2,3,4,4,4]

user_acc_time_data = pd.DataFrame({
    'User Acceptance of Response Times': memory_group_response_time_acc + no_memory_group_response_time_acc,
    'Group': ['Memory'] * len(memory_group_response_time_acc) + ['No Memory'] * len(no_memory_group_response_time_acc)
})

plt.figure(figsize=(8, 6))
sns.boxplot(x='Group', y='User Acceptance of Response Times', data=user_acc_time_data, palette="coolwarm")  # Different color palette
plt.show()
