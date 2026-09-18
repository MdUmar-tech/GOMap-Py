import pandas as pd
import numpy as np

file_path = 'GO_Assignment.txt'

df = pd.read_csv(file_path, delimiter='\t')

# Replace '-' and NaN in 'Column12' and 'Column14'
df['id'].replace({'':np.nan}, inplace=True)


# Drop rows where 'Column2' or 'Column3' is empty
#df.dropna(subset=['Interpro', 'GO'], inplace=True)

#df[['Interpro', 'GO']].replace('', np.nan, inplace=True)
df.dropna(inplace = True)

df.to_csv('GO_Assignment_1.txt', sep='\t', index=False)


