import os
import pandas as pd
from authentication import ws
from calendar import monthrange
from datetime import datetime, timedelta
from azureml.core import Dataset, Datastore, Workspace
from azureml.opendatasets import NoaaIsdWeather

# get workspace and datastore
#ws = Workspace.from_config()
dstore = ws.get_default_datastore()

# adjust parameters as needed
target_years = list(range(2020, 2021))
start_month = 12
state='SEATTLE'

# Get data
for year in target_years:
    for month in range(start_month, 12 + 1):
        for day in range(1,32):
            path = 'pop/{}/{:02d}/{:02d}/'.format(year, month, day)
            try:
                start = datetime(year, month, 1,0,0,0,0)
                end = datetime(year, month, day, 23,59,59,999999)
                isd = NoaaIsdWeather(start, end).to_pandas_dataframe()
                isd = isd[isd['stationName'].str.contains(state, regex=True, na=False)]
                os.makedirs(path, exist_ok=True)
                isd.to_parquet(path + 'data.parquet')
            except Exception as e:
                print('Month {} in year {} likely has no data.\n'.format(month, year))
                print('Exception: {}'.format(e))
