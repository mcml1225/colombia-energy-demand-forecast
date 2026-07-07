"""
run_forecast.py - Main entry point for dynamic forecasting
Always predicts the next 12 months from today
"""

import pandas as pd
from pathlib import Path
from src.preprocessor_simple import SimpleDataPreprocessor
from src.train_model import DemandForecaster
import argparse
from datetime import datetime

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
    print(f"🎯 Will forecast for: next 365 days from today")
    
    # Step 2: Train model
    print("\n🤖 Step 2: Training forecasting model...")
    forecaster = DemandForecaster()
    
    # Use dynamic test size (10% of data, max 365)
    test_size = min(365, len(data) // 10)
    forecaster.train(data, test_size=test_size)
    forecaster.save_model()
    
    # Step 3: Generate predictions for next 365 days from today
    print(f"\n🔮 Step 3: Generating predictions for next 365 days...")
    
    # Start from today
    start_date = pd.Timestamp.now().normalize()
    end_date = start_date + pd.DateOffset(days=365)
    
    print(f"   Period: {start_date.date()} to {end_date.date()}")
    
    # Generate predictions
    predictions = forecaster.predict(periods=365, start_date=start_date)
    
    # Step 4: Save predictions with dynamic filename
    year_from = start_date.year
    year_to = end_date.year
    output_filename = f"forecast_{year_from}_{year_to}.csv"
    output_file = Path(f"predictions/{output_filename}")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(output_file, index=False)
    
    # Step 5: Display summary
    print("\n" + "="*60)
    print(f"FORECAST RESULTS")
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
    export_to_excel(predictions, year_from, year_to, historical_avg, forecast_avg)
    
    return predictions

def export_to_excel(predictions, year_from, year_to, historical_avg, forecast_avg):
    """Export predictions to Excel with summary"""
    output_file = Path(f"predictions/forecast_{year_from}_{year_to}.xlsx")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Daily predictions
        predictions.to_excel(writer, sheet_name='Daily Forecast', index=False)
        
        # Summary
        summary = pd.DataFrame({
            'Metric': [
                'Forecast Period',
                'Prediction Start',
                'Prediction End',
                'Total Days',
                'Average Demand (kWh)',
                'Maximum Demand (kWh)',
                'Minimum Demand (kWh)',
                'Historical Average (kWh)',
                'Expected Growth (%)',
                'Generated On'
            ],
            'Value': [
                f"{year_from} - {year_to}",
                predictions['date'].min().date(),
                predictions['date'].max().date(),
                len(predictions),
                f"{forecast_avg:,.0f}",
                f"{predictions['predicted_demand_kwh'].max():,.0f}",
                f"{predictions['predicted_demand_kwh'].min():,.0f}",
                f"{historical_avg:,.0f}",
                f"{((forecast_avg / historical_avg) - 1) * 100:.1f}%",
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Monthly summary
        predictions['month'] = predictions['date'].dt.month
        predictions['year'] = predictions['date'].dt.year
        monthly = predictions.groupby(['year', 'month'])['predicted_demand_kwh'].agg(['mean', 'min', 'max']).round(0)
        monthly.columns = ['Average', 'Min', 'Max']
        monthly.index.name = 'Year-Month'
        monthly.to_excel(writer, sheet_name='Monthly Summary')
    
    print(f"📊 Excel report saved to: {output_file}")

if __name__ == "__main__":
    main()