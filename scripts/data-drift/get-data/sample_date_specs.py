import os
import pandas as pd
from authentication import ws
from calendar import monthrange
from datetime import datetime, timedelta
from azureml.opendatasets import NoaaIsdWeather
from dateutil import parser
from dateutil.relativedelta import relativedelta

state='SEATTLE'

## One way of specifying dates, by parsing
#end_date = parser.parse('2018-2-28')
#start_date = parser.parse('2018-2-27')

# Yet another way of specifying dates
#start_date = datetime.today() - relativedelta(months=1)
#end_date = datetime.today()

# Yet another way of specifying dates, down to the microsecond
start_date = datetime(2019,1,1,0,0,0,0)
end_date = datetime(2019,1,1,23,59,59,999999)

print(f'start time is: {start_date} and end date is: {end_date}')
isd = NoaaIsdWeather(start_date= start_date, end_date= end_date).to_pandas_dataframe()
isd = isd[ isd['stationName'].str.contains(state, regex=True, na=False)]
print( isd )
