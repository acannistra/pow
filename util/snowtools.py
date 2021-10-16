import requests
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SNOWDATA_URL="https://api.snowobs.com/v1/station/timeseries"
SNOWDATA_TOKEN="71ad26d7aaf410e39efe91bd414d32e1db5d"


def get_snow_df(staid, hours, snow_field = 'snow_depth'):
    # raw = requests.get(url).json()
    # snow = raw['station_timeseries']
    req_params = {
        'token' : SNOWDATA_TOKEN,
        'stid': staid,
        'source': 'nwac',
        'end': datetime.utcnow().strftime("%Y%m%d%H%M"),
        'start': (datetime.utcnow() - timedelta(hours=hours)).strftime("%Y%m%d%H%M")
    }

    raw = requests.get(SNOWDATA_URL, params=req_params)

    obs = raw.json()['station_timeseries']['STATION'][0]['OBSERVATIONS']
    data = pd.DataFrame(
        data=obs
    )

    data = data.set_index(pd.to_datetime(data['date_time']))
    data = data.sort_index()[snow_field]

    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1

    data = data.where(data.between(q1 - 1.5 * iqr,
                                   q3 + 1.5 * iqr), other = np.NaN)
    return(data)

def find_pow(snow, threshold, period):
    accumulation = snow.diff(periods = 1).rolling(period, min_periods=1).sum()
    is_pow = accumulation >= threshold
    all = pd.concat([snow, accumulation, is_pow], axis=1)
    all.columns = ['snow_depth', 'accum', 'is_pow']
    all['accum'] = all['accum'].where(all['accum'] < 100)
    all = all.dropna()
    all.threshold = threshold
    all.period = period
    return(all)


def find_pow_2(snow, threshold, period): 
    accumulation = (snow - snow.shift(periods=period)).dropna()
    is_pow = accumulation >= threshold
    all = pd.concat([snow, accumulation, is_pow], axis=1).dropna()
    all.columns = ['snow_depth', 'accum', 'is_pow']
    all['accum'] = all['accum'].where(abs(all['accum']) < 100)
    all = all.dropna()
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
