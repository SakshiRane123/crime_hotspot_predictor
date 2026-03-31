import pandas as pd

df = pd.read_csv('D:\EDAI_NEW2\EDAI_NEW2\crime-hotspot-predictor\new_dataset_10000.csv')

print(f'Dataset Shape: {df.shape}')
print(f'\nColumns ({len(df.columns)}):')
print(list(df.columns))
print(f'\nSeverity Level Distribution:')
print(df['Severity_Level'].value_counts())
print(f'\nData Types:')
print(df.dtypes)
print(f'\nFirst few rows:')
print(df.head())
