import pandas as pd
df = pd.read_csv('newFileOut.csv')
for i in df:
    print(i)
    if i == 'class':
        break
    if i != 'class' or i != 'index':
        df[i] = df[i].astype('float64')

df['class'][:337] = 3
df['class'][337:779] = 0
df['class'][779:150] = 1
df['class'][1501:2050] = 2
df['class'][2050:2194] = 0
df['class'][2193:3201] = 3
df['class'][3201:3901] = 0
df['class'][4138:4651] = 2
df['class'][4651:] = 3


df = df.dropna()

df.to_csv('output3.csv', index=False)

