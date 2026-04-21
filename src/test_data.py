# Crea un archivo test_data.py
import pandas as pd
from datetime import datetime, timedelta

# Crear datos de prueba
dates = pd.date_range(start='2000-01-01', end='2024-12-31', freq='D')
data = pd.DataFrame({
    'date': dates,
    'demand_kwh': 100000000 + (dates - dates[0]).days * 10000 + np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 5000000,
    'generation_kwh': 98000000 + (dates - dates[0]).days * 9800,
    'unserved_demand_kwh': 0,
    'exports_kwh': 0,
    'imports_kwh': 0
})

# Guardar
data.to_csv('data/processed/colombia_demand_2000_2024.csv', index=False)
print("Test data created!")