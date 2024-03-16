# Overview

Python project for transaction monitoring: 
* 'transaction.py' - main transaction class and methods.
* 'Transaction_monitoring.ipynb' - jupyter notebook (same as app.py) with visualisation and transaction analysis.
* 'app.py' - console app, alternative to notebook.
* 'data' folder - contains two datasets. First dataset is given, it hasn't interesting data for advanced analysis.
  * '/data/sample_orders.csv' - given dataset for analysis.
  * '/data/sample_orders_2.csv' - lightly changed dataset for testing and best performance some of methods.
* 'error_handling_examples.py' - attempt to choose right class-object for transformation of dataset, with error handle. This file is only for demonstration of error handling, was rejected because of best eeror handling from "pandas".

# Setup

```bash
pip install -r requirements.txt
```
# About
This project is processing given CSV file with defined format (containing given columns with given type of data), transform it into dataframe and analyse it. Main goal of analysis is detection and visualisation of suspicious activity.

