"""
run_forecast.py - Main entry point for dynamic forecasting
Always predicts the year after the last available data
"""

import pandas as pd
from pathlib import Path
from src.preprocessor_simple import SimpleDataPreprocessor
from src.train_model import DemandForecaster
import argparse

def main():
    print("="*60)
    print("COLOMBIA ENERGY DEMAND FORECAST - DYNAMIC PREDICTION")
    print("="*60)
    
    # Step 1: Preprocess data
    print("\n📊 Step 1: Loading and preprocessing data...")
    preprocessor = SimpleDataPreprocessor()
    data = preprocessor.run_pipeline()
    
    if data is None or len(data) == 0:
        print("Error: No data available")
        return
    
    # Get last year
    last_year = data['date'].max().year
    next_year = last_year + 1
    
    print(f"\n📅 Data available until: {last_year}")
    print(f"🎯 Will forecast for: {next_year}")
    
    # Step 2: Train model
    print("\n🤖 Step 2: Training forecasting model...")
    forecaster = DemandForecaster()
    
    # Use dynamic test size (10% of data, max 365)
    test_size = min(365, len(data) // 10)
    forecaster.train(data, test_size=test_size)
    forecaster.save_model()
    
    # Step 3: Generate predictions for next year
    print(f"\n🔮 Step 3: Generating predictions for {next_year}...")
    predictions = forecaster.predict(periods=365, last_date=data['date'].max())
    
    # Step 4: Save predictions
    output_file = Path(f"predictions/forecast_{next_year}.csv")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(output_file, index=False)
    
    # Step 5: Display summary
    print("\n" + "="*60)
    print(f"FORECAST RESULTS FOR {next_year}")
    print("="*60)
    print(f"Prediction period: {predictions['date'].min().date()} to {predictions['date'].max().date()}")
    print(f"Total days: {len(predictions)}")
    print(f"\nDemand statistics:")
    print(f"  Average: {predictions['predicted_demand_kwh'].mean():,.0f} kWh")
    print(f"  Maximum: {predictions['predicted_demand_kwh'].max():,.0f} kWh")
    print(f"  Minimum: {predictions['predicted_demand_kwh'].min():,.0f} kWh")
    
    # Growth vs historical
    historical_avg = data['demand_kwh'].mean()
    forecast_avg = predictions['predicted_demand_kwh'].mean()
    growth = ((forecast_avg / historical_avg) - 1) * 100
    print(f"\nExpected growth: {growth:.1f}% vs historical average")
    
    print(f"\n✅ Forecast saved to: {output_file}")
    
    # Optional: Export to Excel
    export_to_excel(predictions, next_year, historical_avg, forecast_avg)
    
    return predictions

def export_to_excel(predictions, year, historical_avg, forecast_avg):
    """Export predictions to Excel with summary"""
    output_file = Path(f"predictions/forecast_{year}.xlsx")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Daily predictions
        predictions.to_excel(writer, sheet_name='Daily Forecast', index=False)
        
        # Summary
        summary = pd.DataFrame({
            'Metric': [
                'Forecast Year',
                'Prediction Start',
                'Prediction End',
                'Total Days',
                'Average Demand (kWh)',
                'Maximum Demand (kWh)',
                'Minimum Demand (kWh)',
                'Historical Average (kWh)',
                'Expected Growth (%)'
            ],
            'Value': [
                year,
                predictions['date'].min().date(),
                predictions['date'].max().date(),
                len(predictions),
                f"{forecast_avg:,.0f}",
                f"{predictions['predicted_demand_kwh'].max():,.0f}",
                f"{predictions['predicted_demand_kwh'].min():,.0f}",
                f"{historical_avg:,.0f}",
                f"{((forecast_avg / historical_avg) - 1) * 100:.1f}%"
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Monthly summary
        predictions['month'] = predictions['date'].dt.month
        monthly = predictions.groupby('month')['predicted_demand_kwh'].agg(['mean', 'min', 'max']).round(0)
        monthly.columns = ['Average', 'Min', 'Max']
        monthly.index.name = 'Month'
        monthly.to_excel(writer, sheet_name='Monthly Summary')
    
    print(f"📊 Excel report saved to: {output_file}")

if __name__ == "__main__":
    main()