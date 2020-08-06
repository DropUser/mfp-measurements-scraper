# mfp-measurements-scraper
A simple web scraper to extract the history of measurements from MyFitnessPal. This leverages the "Edit Previous Entires" page within the Check-In section of the website. This script outputs the data in a comma separated file, sorted by date. It automatically detects and pulls all metrics entered by the user from the Check-In page.

## Setup
This script requires
* [Python 3.8](https://www.python.org/downloads/)
* [pandas 1.10 ](https://pandas.pydata.org/)
* [lxml 4.5.2](https://lxml.de/)
* [requests 2.24.0](https://2.python-requests.org/en/master/)

This may work with other versions, but has only been tested on those specific libraries</br>
To install dependencies, you can run the following statement in your command line</br>
```pip install pandas lxml requests```

## Execution
To run this script, execute it from the command line and provide requested details for Username, Password and Output File Name at the prompt</br>
```python mfp_scraper.py```
