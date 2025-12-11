import numpy as np
import pandas as pd
import plotly.graph_objects as go

ACCENT_COLOR = '#577399'

def to_dict(df: pd.DataFrame) -> dict:
    '''It returns a dicitionary created from df['intensity'].'''
    df2 = df.copy()
    dictio: dict = {}
    y = df2.pop('intensity')
    for index, row in df2.iterrows():
        dictio[row['barri']] = y[index]
    return dictio

def by_day_cat(df: pd.DataFrame) -> pd.DataFrame:
    '''It returns a dataframe with average intensities by barri and day of the week.'''
    df2 = pd.DataFrame()
    df2['barri'] = np.concatenate([df['barri'].unique() for i in range(7)])
    df2['day_cat'] = np.concatenate([np.array([i for barri in df['barri'].unique()]) for i in range(7)])
    df2['intensity'] = np.concatenate([np.array(
        [np.average(df[df['day_cat']==i][df[df['day_cat']==i]['barri']==barri]['intensity'])
        for barri in df['barri'].unique()]) for i in range(7)])
    return df2

def by_barri(df: pd.DataFrame) -> pd.DataFrame:
    '''It returns a dataframe with average intensities by barri.'''
    df2 = pd.DataFrame()
    df2['barri'] = df['barri'].unique()
    df2['intensity'] = [np.average(df[df['barri']==barri]['intensity'])for barri in df['barri'].unique()]
    return df2


def by_day_cat_analysis(df: pd.DataFrame, t) -> go.Figure:
    '''It represents average excess of intensity by day of the week as percentage. It returns variances of these averages.'''
    df2 = df.copy()
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
    weekdays = t("weekdays")

    trace = go.Scatter(
        x=weekdays,
        y=averages,
        mode='markers', # Display points (equivalent to Matplotlib's fmt="o")
        marker=dict(size=10, color=ACCENT_COLOR),
        error_y=dict(
            type='data',
            array=np.sqrt(variances), # The values for the error bars
            visible=True,
            thickness=1.5,
            width=5 
        ),
        name='Average Intensity'
    )

    fig = go.Figure(data=[trace])

    fig.update_layout(
        title=t("dotw_i_excess"),
        xaxis_title=t("day"),
        yaxis_title=f"{t("i_excess")}(%)",
        template="plotly_white" # Optional: provides a clean white background
    )
    return fig

