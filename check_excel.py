import pandas as pd
try:
    df = pd.read_excel('liste personnel.xlsx')
    print(df.columns.tolist())
    print(df.head())
except Exception as e:
    print(f"Error: {e}")
