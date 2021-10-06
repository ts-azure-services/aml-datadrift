import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from authentication import ws
from azureml.core import Dataset
from datetime import datetime
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.datadrift import DataDriftDetector, AlertConfiguration
from azureml.data import DataType

# Load data, and register target
def data_load_to_blob(input_dataset=None, blob_header=None):
    dstore = ws.get_default_datastore()
    dstore.upload(input_dataset, blob_header, overwrite=True, show_progress=True)
    print(f'Data load complete.')

def create_baseline_and_target(blob_header=None, target_name=None, baseline_name=None):
    dstore = ws.get_default_datastore()
    target_datapath = [(dstore, blob_header + '/2020/*/*/data.parquet')]
    baseline_datapath = [(dstore, blob_header + '/2019/*/*/data.parquet')]
    partition_format = blob_header + '/{partition_time:yyyy/mm/dd}/data.parquet'

    # Create target dataset
    target_tabular = Dataset.Tabular.from_parquet_files(path=target_datapath, partition_format = partition_format)
    tsd = target_tabular.with_timestamp_columns('partition_time')
    target = tsd.register(ws, target_name, create_new_version=True,
            description='Data for Tabular Dataset with time series',
            tags={'type':'TabularDataset'}
            )

    # Create baseline dataset
    baseline_tabular = Dataset.Tabular.from_parquet_files(path = baseline_datapath, partition_format = partition_format)
    bsd = baseline_tabular.with_timestamp_columns('partition_time')
    baseline = bsd.register(ws, baseline_name, create_new_version=True,
            description='Data for Tabular Dataset with time series',
            tags={'type':'TabularDataset'}
            )
    return target, baseline

def select_features(tabular_dataset=None):
    columns  = list(tabular_dataset.take(1).to_pandas_dataframe())
    exclude  = ['year', 'day', 'version', '__index_level_0__', 'usaf', 'wban']
    features = [col for col in columns if col not in exclude]
    return features


# Get dataset monitor
def get_dataset_monitor(ws=None, name=None, baseline=None, target=None, compute_target=None, features=None):
    dataset_monitor_name = name
    try:
        monitor = DataDriftDetector.get_by_name(ws, dataset_monitor_name)
        print(f'Found the dataset monitor called: {dataset_monitor_name}')
    except:
        alert_config = AlertConfiguration(['joeyemail@gmail.com']) # replace with your email to recieve alerts from the scheduled pipeline after enabling
        monitor = DataDriftDetector.create_from_datasets(
            ws, dataset_monitor_name, baseline, target,
            compute_target=compute_target, 
          frequency='Week',# how often to analyze target data
          feature_list=features,                
          drift_threshold=None,# threshold from 0 to 1 for email alerting
          latency=0,# SLA in hours for target data to arrive in the dataset
          alert_config=alert_config)
        print(f'Created the dataset monitor called {dataset_monitor_name}')
    return monitor


def trigger_run(monitor=None):
    ## update the feature list
    #monitor  = monitor.update(feature_list=features)

    # Trigger run for backfill for one month
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2020, 3, 31)
    backfill = monitor.backfill(start_date, end_date)

    # make sure the backfill has completed
    backfill.wait_for_completion(wait_post_processing=True)


if __name__ == "__main__":
    blob_header='SEATTLE'
    data_load_to_blob(input_dataset='./seattle-weather-data', blob_header=blob_header)
    target, baseline = create_baseline_and_target(
            blob_header=blob_header, 
            target_name='seattle-weather-target',
            baseline_name='seattle-weather-baseline'
            )
    features = select_features(tabular_dataset=target)
    monitor = get_dataset_monitor(ws=ws, 
            name='seattle-weather-datadrift', 
            baseline=baseline,
            target=target,
            compute_target='gpu-cluster',
            features=features
            )
    trigger_run(monitor=monitor)

