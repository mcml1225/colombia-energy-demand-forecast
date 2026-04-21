# En main.py, en la función run_pipeline, después de entrenar el modelo:

# STEP 4: Generate predictions
if predict:
    print("\n🔮 STEP 4: Generating future predictions...")
    forecaster = DemandForecaster()
    forecaster.load_model()
    
    # Get last date from historical data
    last_historical_date = data['date'].max()
    print(f"   Last data date: {last_historical_date.date()}")
    print(f"   Predicting for year: {last_historical_date.year + 1}")
    
    # Generate predictions for next year
    predictions = forecaster.predict(periods=365, last_date=last_historical_date)
    
    # Save predictions
    output_path = Path(f"predictions/forecast_{last_historical_date.year + 1}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(output_path, index=False)
    print(f"✓ Predictions saved to {output_path}")
    
    # Display summary
    print("\n📊 PREDICTIONS SUMMARY:")
    print(f"  Predicting for: {predictions['date'].min().year}")
    print(f"  Period: {predictions['date'].min().date()} to {predictions['date'].max().date()}")
    print(f"  Average predicted demand: {predictions['predicted_demand_kwh'].mean():,.0f} kWh")
    print(f"  Max predicted demand: {predictions['predicted_demand_kwh'].max():,.0f} kWh")
    print(f"  Min predicted demand: {predictions['predicted_demand_kwh'].min():,.0f} kWh")