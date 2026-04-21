"""
View prediction statistics
"""

import pandas as pd

# Load predictions
df = pd.read_csv('predictions/forecast_2025.csv')

print("=" * 50)
print("PREDICCIONES DE DEMANDA ENERGÉTICA 2025")
print("=" * 50)

print(f"\nTotal días pronosticados: {len(df)}")

print(f"\nDemanda promedio: {df['predicted_demand_kwh'].mean():,.0f} kWh")
print(f"Demanda máxima: {df['predicted_demand_kwh'].max():,.0f} kWh")
print(f"Demanda mínima: {df['predicted_demand_kwh'].min():,.0f} kWh")

print(f"\nRango de predicción:")
print(f"  Límite inferior promedio: {df['lower_bound_kwh'].mean():,.0f} kWh")
print(f"  Límite superior promedio: {df['upper_bound_kwh'].mean():,.0f} kWh")

print("\n" + "=" * 50)
print("PRIMERAS 10 PREDICCIONES:")
print("=" * 50)
print(df[['date', 'predicted_demand_kwh']].head(10).to_string(index=False))

print("\n" + "=" * 50)
print("ÚLTIMAS 10 PREDICCIONES:")
print("=" * 50)
print(df[['date', 'predicted_demand_kwh']].tail(10).to_string(index=False))

# Encontrar picos
max_idx = df['predicted_demand_kwh'].idxmax()
min_idx = df['predicted_demand_kwh'].idxmin()

print("\n" + "=" * 50)
print("PUNTOS CRÍTICOS:")
print("=" * 50)
print(f"Día de mayor demanda: {df.loc[max_idx, 'date']} - {df.loc[max_idx, 'predicted_demand_kwh']:,.0f} kWh")
print(f"Día de menor demanda: {df.loc[min_idx, 'date']} - {df.loc[min_idx, 'predicted_demand_kwh']:,.0f} kWh")