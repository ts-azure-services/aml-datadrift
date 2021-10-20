# Intent 
- A repo to expose some examples of 'data drift' in Azure Machine Learning

# Steps
- First ensure you have a file called ```sub.env``` in the './scripts' folder with the following line: ```SUB_ID=<your subscription id>```
- Then run the ```create-workspace-sprbac.sh``` shell script to create the AML workspace
	- This will also create two environment files: ```config.json``` and ```variables.env``` which will help with service principal authentication and be used in the ```authentication.py``` script.
	- As part of the ```create-workspace-sprbac.sh``` script, names are derived based upon a random choice combining the ```nouns.txt``` and the ```adjectives.txt``` file, implemented in the ```random_name.py``` script.
- In the './data-drift' folder, run the ```clusters.py``` script to create a cluster.
- The 'get-data' folder contains some scripts for pulling data from Azure Open Datasets.
- The 'seattle-weather-data' folder contains pre-downloaded files for the 2018-2020 Seattle NOAA Weather Data.
- To trigger the data drift monitor for the Seattle Weather, run ```seattle_weather_drift.py```.
- To trigger the data drift monitor for the US County data, run ```us_county_drift.py```.

# Other
- If on Mac, ```brew install libomp```, refer [article](https://stackoverflow.com/questions/44937698/lightgbm-oserror-library-not-loaded)
- While the clusters.py is more of a setup script, to allow for interaction with the variables.env file, have
  stored this under the ```data-drift``` folder.
