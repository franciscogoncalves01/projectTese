import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

speech_recognizer = [3,4,4,4,3,4, 2,2,4,5,4,4]
speech_generator = [4,5,5,4,3,5, 4,4,3,4,5,3]
elmo_voice = [4,5,5,4,4,5, 4,4,3,4,5,4]

user_data = pd.DataFrame({
    'User Evaluation Score': speech_recognizer + speech_generator + elmo_voice,
    'Item': ['I3'] * len(speech_recognizer) + ['I4'] * len(speech_generator) + ['I5'] * len(elmo_voice)
})

# Create a box plot for Ended Interactions
plt.figure(figsize=(8, 6))
sns.boxplot(x='Item', y='User Evaluation Score', data=user_data, palette="coolwarm")  # Different color palette
plt.show()
