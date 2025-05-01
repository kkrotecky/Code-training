import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Loading the data
df = pd.read_csv('countries.csv')
# Displaying the first few rows of the DataFrame
# df.head() will show the first 5 rows of the DataFrame, which includes the columns 'Country', 'Capital', 'Population', and 'Area'.
# This gives a quick overview of the data structure and the first few entries.

print(df.head())

# Displaying the shape of the DataFrame
# df.shape will return a tuple representing the dimensions of the DataFrame, i.e., the number of rows and columns.  
# This is useful to understand the size of the dataset.
# The shape of the DataFrame will be printed to the console.
# The output will be a tuple indicating the number of rows and columns in the DataFrame.
# For example, (100, 4) indicates 100 rows and 4 columns.
print(df.shape)

