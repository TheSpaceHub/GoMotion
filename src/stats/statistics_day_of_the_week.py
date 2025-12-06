import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def to_dict(df):
    '''It returns a dicitionary created from df['intensity'].'''
    df2 = df.copy()
    dictio: dict = {}
    y = df2.pop('intensity')
    for index, row in df2.iterrows():
        dictio[row['barri']] = y[index]
    return dictio

def by_day_cat(df):
    '''It returns a dataframe with average intensities by barri and day of the week.'''
    df2 = pd.DataFrame()
    df2['barri'] = np.concatenate([df['barri'].unique() for i in range(7)])
    df2['day_cat'] = np.concatenate([np.array([i for barri in df['barri'].unique()]) for i in range(7)])
    df2['intensity'] = np.concatenate([np.array(
        [np.average(df[df['day_cat']==i][df[df['day_cat']==i]['barri']==barri]['intensity'])
        for barri in df['barri'].unique()]) for i in range(7)])
    return df2

def by_barri(df):
    '''It returns a dataframe with average intensities by barri.'''
    df2 = pd.DataFrame()
    df2['barri'] = df['barri'].unique()
    df2['intensity'] = [np.average(df[df['barri']==barri]['intensity'])for barri in df['barri'].unique()]
    return df2


def by_day_cat_analysis(df):
    '''It represents average excess of intensity by day of the week as percentage. It returns variances of these averages.'''
    df2 = df.copy()
    df2 = pd.read_csv('data/data_processed.csv')
    weekdays = {'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3, 'Viernes': 4, 'Sábado': 5, 'Domingo': 6}
    df2['day_cat'] = [weekdays[x] for x in df['day_cat']]
    df2['intensity'] = np.log(df['intensity'])
    dictio = to_dict(by_barri(df2))
    df3 = by_day_cat(df2)
    df3['intensity'] = df3['intensity'] - [dictio[x] for x in df3['barri']]
    df3['intensity'] = 100*(np.exp(df3['intensity'])-1)
    averages = [np.average(np.array([row['intensity'] for _, row in df3.iterrows()
                                  if row['day_cat']==day])) for day in range(7)]
    variances = [np.var(np.array([row['intensity'] for _, row in df3.iterrows()
                                  if row['day_cat']==day])) for day in range(7)]
    weekdays = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    plt.errorbar(weekdays, averages, yerr=np.sqrt(variances), fmt="o")
    plt.xlabel("Día")
    plt.ylabel("Exceso de intensidad(%)")
    plt.savefig("by_day_cat.png")
    return variances

df = pd.read_csv('data/data_processed.csv')
by_day_cat_analysis(df)
