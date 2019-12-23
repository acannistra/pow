import requests
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def get_nwac_v2_url(staid, datetime_now = datetime.isoformat(datetime.now()), limit=168):
    return("https://www.nwac.us/api/v5/measurement?data_logger={}&max_datetime={}&limit={}".format(staid, datetime_now, limit))

def get_snow_df(url, snow_field = 'snow_depth'):
    # raw = requests.get(url).json()
    # snow = raw['station_timeseries']
    raw = requests.get(url, headers={'Authorization': "Token d8d0db6e9d8ec1d699cbe4acf1052e72716f9bee"}).json()

    data = json_normalize(raw['results'])
    data = data.set_index(pd.to_datetime(data.datetime))
    data = data.sort_index()[snow_field]
    # data = data.where(data != data.max(),
    #                   other=np.NaN)
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1

    data = data.where(data.between(q1 - 1.5 * iqr,
                                   q3 + 1.5 * iqr), other = np.NaN)
    return(data)

def find_pow(snow, threshold, period):
    accumulation = snow.diff(periods = 1).rolling(period, min_periods=1).sum()
    is_pow = accumulation > threshold
    all = pd.concat([snow, accumulation, is_pow], axis=1)
    all.columns = ['snow_depth', 'accum', 'is_pow']
    all.threshold = threshold
    all.period = period
    return(all)

def pow_history(pow_df, station):
    fig, ax = plt.subplots(figsize=(10,8))
    pow_df.accum.plot(ax = ax)
    ax.set_xlabel("Time")
    ax.set_title(station, fontdict={'fontweight':'bold'}, loc='left')
    ax.set_title("Period: {}h, Threshold: {}in, Computed {}".format(pow_df.period, pow_df.threshold, datetime.now().strftime("%m/%d/%Y %H:%M:%S")),
              loc='right',
              fontdict={'fontsize':'small', 'fontweight':'light'})
    ax.set_ylabel("Accumulation [in]")
    [ax.axvspan(a, a - timedelta(hours=1), facecolor='red', edgecolor=None, alpha=0.5) for a in pow_df[pow_df.is_pow].index]
    return fig
