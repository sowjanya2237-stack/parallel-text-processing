import pandas as pd

# Read the CSV file
data = pd.read_csv("Reviews.csv")

# Select only the text column
text_column = data["Text"]

# Save it to a new CSV file (optional)
text_column.to_csv("text_only.txt", index=False)

# Print the text column
print(text_column)