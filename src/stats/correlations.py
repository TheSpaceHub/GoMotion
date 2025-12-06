import numpy as np
import pandas as pd

def to_dict(df, aux):
    df2 = df.copy()
    dictio: dict = {}
    y = df2.pop('intensity')
    for index, row in df2.iterrows():
        dictio[(row['barri'], row[aux])] = y[index]
    return dictio

def by_month(df):
    '''It returns a dataframe with average intensities by barri and month.'''
    df2 = pd.DataFrame()
    df2['barri'] = np.concatenate([df['barri'].unique() for i in range(1, 13)])
    df2['month'] = np.concatenate([np.array([i for barri in df['barri'].unique()]) for i in range(1, 13)])
    df2['intensity'] = np.concatenate([np.array([np.average(df[df['month']==i][df[df['month']==i]['barri']==barri]['intensity']) for barri in df['barri'].unique()]) for i in range(1, 13)])
    return df2

def by_day_of_week(df):
    '''It returns a dataframe with average intensities by barri and day of the week.'''
    df2 = pd.DataFrame()
    df2['barri'] = np.concatenate([df['barri'].unique() for i in range(7)])
    df2['day_cat'] = np.concatenate([np.array([i for barri in df['barri'].unique()]) for i in range(7)])
    df2['intensity'] = np.concatenate([np.array([np.average(df[df['day_cat']==i][df[df['day_cat']==i]['barri']==barri]['intensity']) for barri in df['barri'].unique()]) for i in range(7)])
    return df2

def intensity_variances_by_barri(df):
    '''It returns intensity's variancies by barri.'''
    df2 = pd.DataFrame()
    df2['barri'] = df['barri'].unique()
    df2['variance'] = [np.var(np.array([row['intensity'] for _, row in df.iterrows() if row['barri']==barri])) for barri in df['barri'].unique()]
    return df2

def clean_day_cat(df):
    '''It returns a dataframe where intensity is replaced by the diference between original registered intensity 
    and barri's average intensity.'''
    dictio: dict = to_dict(by_day_of_week(df), 'day_cat')
    df2 = df.copy()
    df2['intensity'] = [row['intensity']-dictio[(row['barri'], row['day_cat'])] for _, row in df2.iterrows()]
    return df2

def clean_month(df):
    '''It removes month effect from intensity.'''
    dictio: dict = to_dict(by_month(df), 'month')
    df2 = df.copy()
    df2['intensity'] = [row['intensity']-dictio[(row['barri'], row['month'])] for _, row in df2.iterrows()]
    return df2

def process_df(df):
    '''It removes month and day of week effect from intensity. Intensity is converted to
    logarithm of intensity.'''
    weekdays = {'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3, 'Viernes': 4, 'Sábado': 5, 'Domingo': 6}
    df['day_cat'] = [weekdays[x] for x in df['day_cat']]
    df['intensity'] = np.log(df['intensity'])
    return clean_month(clean_day_cat(df))

def get_correlations():
    '''Gets correlations between max_temp and intensity, min_temp and intensity and precipitation and intensity'''
    df_og=pd.read_csv('data/data_processed.csv')
    df_og["month"] = [int(x) for x in df_og["month_cat"]]
    df = process_df(df_og)
    maxt_int = np.corrcoef(df['intensity'], df['temperature_2m_max'])[0][1]
    mint_int = np.corrcoef(df['intensity'], df['temperature_2m_min'])[0][1]
    prec_int = np.corrcoef(df['intensity'], df['precipitation_sum'])[0][1]
    print(f"Correlación entre temperatura máxima e intensidad: {maxt_int}.")
    print(f"Correlación entre temperatura mínima e intensidad: {mint_int}.")
    print(f"Correlación entre precipitación e intensidad: {prec_int}.")
    return maxt_int, mint_int, prec_int