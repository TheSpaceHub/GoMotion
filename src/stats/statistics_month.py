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

def by_month(df: pd.DataFrame) -> pd.DataFrame:
    '''It returns a dataframe with average intensities by barri and month.'''
    df2 = pd.DataFrame()
    df2['barri'] = np.concatenate([df['barri'].unique() for i in range(1, 13)])
    df2['month'] = np.concatenate([np.array([i for barri in df['barri'].unique()]) for i in range(1, 13)])
    df2['intensity'] = np.concatenate([np.array(
        [np.average(df[df['month']==i][df[df['month']==i]['barri']==barri]['intensity'])
        for barri in df['barri'].unique()]) for i in range(1, 13)])
    return df2

def by_barri(df: pd.DataFrame) -> pd.DataFrame:
    '''It returns a dataframe with average intensities by barri.'''
    df2 = pd.DataFrame()
    df2['barri'] = df['barri'].unique()
    df2['intensity'] = [np.average(df[df['barri']==barri]['intensity'])for barri in df['barri'].unique()]
    return df2


def by_month_analysis(df: pd.DataFrame, t) -> go.Figure:
    '''It represents average excess of intensity by month as percentage. It returns variances of these averages.'''
    df["month"] = [int(x) for x in df["month_cat"]]
    df2 = df.copy()
    df2 = pd.read_csv('data/data_processed.csv')
    df2["month"] = [int(x) for x in df2["month_cat"]]
    df2['intensity'] = np.log(df['intensity'])
    dictio = to_dict(by_barri(df2))
    df3 = by_month(df2)
    df3['intensity'] = df3['intensity'] - [dictio[x] for x in df3['barri']]
    df3['intensity'] = 100*(np.exp(df3['intensity'])-1)
    averages = [np.average(np.array([row['intensity'] for _, row in df3.iterrows()
                                  if row['month']==month])) for month in range(1, 13)]
    variances = [np.var(np.array([row['intensity'] for _, row in df3.iterrows()
                                  if row['month']==month])) for month in range(1, 13)]
    months = t("months")

    trace = go.Scatter(
        x=months,
        y=averages,
        mode='markers',
        marker=dict(size=10, color=ACCENT_COLOR),
        error_y=dict(
            type='data',
            array=np.sqrt(variances),
            visible=True,
            thickness=1.5,
            width=5
        ),
        name='Average Intensity'
    )

    # 2. Create the Figure object and apply layout
    fig = go.Figure(data=[trace])

    fig.update_layout(
        title=t("month_i_excess"),
        xaxis_title=t("month"),
        yaxis_title=f"{t("i_excess")}(%)",
        template="plotly_white"
    )

    return fig, variances


