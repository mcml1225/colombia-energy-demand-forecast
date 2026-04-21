"""
show_predictions.py - Display latest predictions
"""

import pandas as pd
from pathlib import Path

# Find the latest prediction file
prediction_files = list(Path('predictions').glob('forecast_*.csv'))
if not prediction_files:
    print("No prediction files found. Run run_forecast.py first.")
    exit()

# Get the most recent (highest year)
latest_file = max(prediction_files, key=lambda x: int(x.stem.split('_')[1]))
df = pd.read_csv(latest_file)
df['date'] = pd.to_datetime(df['date'])

year = df['date'].min().year

print('='*60)
print(f'PREDICCIONES DEMANDA ENERGÉTICA COLOMBIA {year}')
print('='*60)
print(f'Período: {df["date"].min().date()} a {df["date"].max().date()}')
print(f'Días pronosticados: {len(df)}')
print(f'\nDemanda promedio diaria: {df["predicted_demand_kwh"].mean():,.0f} kWh')
print(f'Demanda máxima: {df["predicted_demand_kwh"].max():,.0f} kWh')
print(f'Demanda mínima: {df["predicted_demand_kwh"].min():,.0f} kWh')

print(f'\nPrimeras 10 predicciones:')
print(df[['date', 'predicted_demand_kwh']].head(10).to_string(index=False))