"""
Test only the preprocessor
"""

from src.preprocessor import DataPreprocessor

print("Testing preprocessor...")
preprocessor = DataPreprocessor()
data = preprocessor.run_pipeline()

if data is not None:
    print(f"\n✓ Success! Loaded {len(data)} records")
    print(f"Date range: {data['date'].min()} to {data['date'].max()}")
    print(f"\nFirst 5 rows:")
    print(data[['date', 'demand_kwh', 'generation_kwh']].head())
    print(f"\nLast 5 rows:")
    print(data[['date', 'demand_kwh', 'generation_kwh']].tail())
else:
    print("Failed to load data")