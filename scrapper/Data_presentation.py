import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Loading the data
countries_data = pd.read_csv('scrapper/countries.csv')

# Set Seaborn style
sns.set_theme(style="whitegrid")

# Plot the top 10 biggest countries by Area (in thousands of sq km)
if 'Area' not in countries_data.columns:
    raise ValueError("The 'Area' column is missing from the dataset.")
if not pd.api.types.is_numeric_dtype(countries_data['Area']):
    raise ValueError("The 'Area' column must contain numeric data.")

top_countries = countries_data.sort_values(by='Area', ascending=False).head(10)

# Add a category column for hue
top_countries = top_countries.copy()
top_countries['Top3'] = ['Top 3'] * 3 + ['Others'] * (len(top_countries) - 3)

plt.figure(figsize=(10, 6))
sns.barplot(
    data=top_countries,
    y='Country',
    x=top_countries['Area'] / 1000,
    hue='Top3',  # Use the new category column
    dodge=False,  # Bars overlap, so set to False for single bars
    palette={'Top 3': 'red', 'Others': 'yellow'}
)
plt.xlabel('Area (thousands of sq km)')
plt.title('Top 10 Biggest Countries by Area')
plt.tight_layout()
plt.show()