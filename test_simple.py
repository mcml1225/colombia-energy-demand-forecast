"""
Test simple preprocessor
"""

from src.preprocessor_simple import SimpleDataPreprocessor

print("Testing simple preprocessor...")
preprocessor = SimpleDataPreprocessor()
data = preprocessor.run_pipeline()

if data is not None:
    print(f"\n✓ Success! Loaded {len(data)} records")
    print(f"Date range: {data['date'].min()} to {data['date'].max()}")
    print(f"\nFirst 10 rows of data:")
    print(data[['date', 'demand_kwh']].head(10))
    print(f"\nData types:")
    print(data.dtypes)