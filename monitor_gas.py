import pandas as pd

url = "https://docs.google.com/spreadsheets/d/18bzSR5JAIGhiISITbEMehDAWRVXMJqUNbqXeTmYLttM/export?format=csv&gid=325699321"

df = pd.read_csv(url)

print(df.head())
print(df.columns.tolist())
