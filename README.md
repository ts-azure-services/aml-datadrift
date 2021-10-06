# Intent 
- A repo to expose some examples of 'data drift' in Azure Machine Learning

# File Structure
- LICENSE.TXT
- README.md
- requirements.txt
- scripts:
	- "Setup scripts"
		- authentication.py ```Used to authenticate the workspace with a service principal```
		- create-workspace-sprbac.sh ```shell script to create AML workspace```
		- config.json ```created as part of the initial AML workspace setup```
		- sub.env ```subscription info: needs to be in place prior to execution```
			- Manually create a file called ```sub.env``` with one line: ```SUB_ID="<enter subscription id>"```
		- variables.env ```gets created during workflow, for authentication```
		- data-drift:
			- clusters.py ```script to provision a CPU cluster```
			- drift.yaml ```sample data drift yaml file```
			- get-data ```scripts to get data from Azure Open Datasets```
			- seattle-weather-data ```folder that captures 2018-2020 seattle NOAA weather data```
			- seattle_weather_drift.py ```script to trigger Seattle weather data drift monitor```
			- us_county_drift.py ```script to trigger US county data drift monitor```
		- name-generator
			- adjectives.txt ```used as input into random_name.py```
			- nouns.txt ```used as input into random_name.py```
			- random_name.py ```uses adjectives.txt. and nouns.txt to create a random name```

# Other
- If on Mac, ```brew install libomp```, refer [article](https://stackoverflow.com/questions/44937698/lightgbm-oserror-library-not-loaded)
- While the clusters.py is more of a setup script, to allow for interaction with the variables.env file, have
  stored this under the ```data-drift``` folder
