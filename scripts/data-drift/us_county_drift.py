import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import pandas as pd
from authentication import ws
from azureml.core import Dataset
from datetime import datetime
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.datadrift import DataDriftDetector, AlertConfiguration
from azureml.data import DataType
from azureml.opendatasets import UsPopulationCounty

def create_baseline_and_target():
    def_blob_store = ws.get_default_datastore()
    dp = (def_blob_store, '/input-dataframes')
    
    # Get US County dataset
    population = UsPopulationCounty()
    df = population.to_pandas_dataframe()

    # Get dataset structure
    print( df.info() )

    # Add the datetime to the data for both census periods //not making a virtual column
    df['dtcol'] = pd.to_datetime(dict(year=df.decennialTime, month=1, day=1))

    # Make the most recent census the target, the prior = baseline, and register it
    # Create baseline and target dataframes
    bdf = df [ df['dtcol'] == '2000-01-01' ].copy()
    tdf = df [ df['dtcol'] == '2010-01-01' ].copy()

    # Register dataframes as datasets
    baseline_dataset = Dataset.Tabular.register_pandas_dataframe(dataframe = bdf, target=dp, name='baseline_dataframe')
    target_dataset = Dataset.Tabular.register_pandas_dataframe(dataframe = tdf, target=dp, name='target_dataframe')

    # Create a dataset monitor with the above two as specifications
    bsd = baseline_dataset.with_timestamp_columns('dtcol')
    tsd = target_dataset.with_timestamp_columns('dtcol')

    # Register these tabular/time series datasets
    baseline = bsd.register(ws, 'baseline', create_new_version=True, description='Baseline dataset for US County Population (2000)')
    target = tsd.register(ws, 'target', create_new_version=True, description='Target dataset for US County Population (2010)')
    return baseline, target, bdf

def select_features(df=None):
    ## create feature list - need to exclude columns that naturally drift or increment over time, such as year, day, index
    column_values = list(df.columns)
    exclude  = ['decennialTime']
    features = [col for col in column_values if col not in exclude]
    return features

# Get dataset monitor
def create_dataset_monitor(ws=None, name=None, baseline=None, target=None, compute_target=None, features=None):
    dataset_monitor_name = name
    try:
        monitor = DataDriftDetector.get_by_name(ws, dataset_monitor_name)
        print(f'Found the dataset monitor called: {dataset_monitor_name}')
    except:
        alert_config = AlertConfiguration(['emailid@gmail.com']) # replace with your email to recieve alerts from the scheduled pipeline after enabling
        monitor = DataDriftDetector.create_from_datasets(
            ws, dataset_monitor_name, baseline, target,
            compute_target=compute_target,         # compute target for scheduled pipeline and backfills 
          frequency='Week',                     # how often to analyze target data
          feature_list=features,                    # list of features to detect drift on
          drift_threshold=None,                 # threshold from 0 to 1 for email alerting
          latency=0,                            # SLA in hours for target data to arrive in the dataset
          alert_config=alert_config)
        print(f'Created the dataset monitor called {dataset_monitor_name}')
    return monitor

def trigger_run(monitor=None):
    ## update the feature list
    #monitor  = monitor.update(feature_list=features)

    # Trigger run for backfill for one month
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2010, 1, 1)
    backfill = monitor.backfill(start_date, end_date)

    # make sure the backfill has completed
    backfill.wait_for_completion(wait_post_processing=True)

if __name__ == "__main__":
    baseline, target, bdf = create_baseline_and_target()
    features = select_features(bdf)
    monitor = create_dataset_monitor(
            ws=ws, 
            name='us_county_pop_datadrift', 
            baseline=baseline, 
            target=target,
            compute_target='gpu-cluster',
            features=features
            )
    trigger_run(monitor=monitor)

