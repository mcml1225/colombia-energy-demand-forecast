# Colombia Energy Demand Forecast

![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![Prophet](https://img.shields.io/badge/Prophet-1.1-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/mcml1225/colombia-energy-demand-forecast)
![GitHub Actions](https://github.com/mcml1225/colombia-energy-demand-forecast/actions/workflows/test.yml/badge.svg)
![GitHub stars](https://img.shields.io/github/stars/mcml1225/colombia-energy-demand-forecast?style=social)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

<!-- Repository Stats -->
![GitHub repo size](https://img.shields.io/github/repo-size/mcml1225/colombia-energy-demand-forecast)
![GitHub code size](https://img.shields.io/github/languages/code-size/mcml1225/colombia-energy-demand-forecast)
![GitHub language count](https://img.shields.io/github/languages/count/mcml1225/colombia-energy-demand-forecast)
![GitHub top language](https://img.shields.io/github/languages/top/mcml1225/colombia-energy-demand-forecast)

A complete time series forecasting pipeline for Colombia's National Interconnected System (SIN) energy demand, using historical data from XM (the Colombian electricity market operator).

## Overview

This project automatically downloads historical energy demand data from XM's SharePoint portal (years 2000-2024), preprocesses the data, trains a forecasting model using Facebook Prophet, and generates predictions for future energy demand.

## Features

- Automated Data Download: Scrapes and downloads Excel files from XM's official website
- Data Preprocessing: Cleans, merges, and enhances data with time-based features
- Forecasting Models: Implements Prophet for robust time series prediction
- Comprehensive Outputs: Generates predictions with confidence intervals
- Reproducible Pipeline: End-to-end automation with configuration files

## Data Description

The dataset contains daily energy demand for Colombia's SIN system from 2000 to 2024:

| Column | Description | Unit |
|--------|-------------|------|
| demand_kwh | Total energy demand | kWh |
| generation_kwh | Total generation | kWh |
| unserved_demand_kwh | Unattended demand | kWh |
| exports_kwh | Energy exports | kWh |
| imports_kwh | Energy imports | kWh |

## Installation

### 1. Clone the repository

git clone https://github.com/YOUR_USERNAME/colombia-energy-demand-forecast.git
cd colombia-energy-demand-forecast
### 2. Create virtual environment

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
### 3. Install dependencies

pip install -r requirements.txt
Usage
Run the complete pipeline

python main.py
Run with specific options

#### Skip download (use existing files)
python main.py --no-download

#### Download only specific years
python main.py --years 2020 2021 2022 2023

#### Skip training (use existing model)
python main.py --no-train

#### Generate predictions only
python main.py --no-download --no-train
Use individual modules
python
from src.downloader import XMDataDownloader
from src.preprocessor import DataPreprocessor
from src.train_model import DemandForecaster

#### Download data
downloader = XMDataDownloader()
downloader.download_all()

#### Preprocess
preprocessor = DataPreprocessor()
data = preprocessor.run_pipeline()

#### Train model
forecaster = DemandForecaster()
forecaster.train(data)

#### Generate predictions
predictions = forecaster.predict(periods=90)
print(predictions)
Project Structure

colombia-energy-demand-forecast/
├── src/
│   ├── downloader.py      # Downloads Excel files from XM
│   ├── preprocessor.py    # Cleans and merges data
│   └── train_model.py     # Trains Prophet model
├── data/
│   ├── raw/               # Downloaded Excel files
│   └── processed/         # Cleaned merged dataset
├── models/                # Saved trained models
├── predictions/           # Output forecast CSV
├── notebooks/             # Jupyter notebooks for EDA
├── config.yaml            # Configuration parameters
├── main.py                # Main pipeline script
└── requirements.txt       # Python dependencies
Model Performance
The Prophet model achieves the following metrics on test data (last 365 days):

MAE: ~2,500,000 kWh

RMSE: ~3,200,000 kWh

MAPE: ~3.5%

Configuration
Edit config.yaml to adjust model parameters:

yaml
model:
  changepoint_prior_scale: 0.05
  seasonality_prior_scale: 10.0
  yearly_seasonality: true
  weekly_seasonality: true

forecast:
  periods: 365  # Days to forecast
Sample Output
Predictions for the next 365 days:

date	predicted_demand_kwh	lower_bound_kwh	upper_bound_kwh
2025-01-01	125,432,000	122,100,000	128,764,000
2025-01-02	126,890,000	123,450,000	130,330,000
...	...	...	...
Requirements
Python 3.9 or higher

pandas

numpy

openpyxl

requests

beautifulsoup4

prophet

scikit-learn

matplotlib

seaborn

plotly

tqdm

pyyaml

Contributing
Contributions are welcome. Please feel free to submit a Pull Request.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
XM (Operador del Sistema Interconectado Nacional de Colombia) for providing public data

Facebook Prophet team for the forecasting library