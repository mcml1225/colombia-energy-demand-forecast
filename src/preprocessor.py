"""
preprocessor.py - Main preprocessor for energy demand data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob

class DataPreprocessor:
    """
    Loads, cleans, and merges all Excel files from XM
    """
    
    def __init__(self, raw_path="data/raw/", processed_path="data/processed/"):
        self.raw_path = Path(raw_path)
        self.processed_path = Path(processed_path)
        self.processed_path.mkdir(parents=True, exist_ok=True)
        
    def load_excel_file(self, filepath):
        """Load a single Excel file"""
        try:
            # Read Excel with skiprows=3 (based on inspection)
            df = pd.read_excel(filepath, skiprows=3)
            
            # Rename columns
            df = df.rename(columns={
                'Fecha': 'date',
                'Demanda Energia SIN kWh': 'demand_kwh',
                'Generación kWh': 'generation_kwh',
                'Demanda No Atendida kWh': 'unserved_demand_kwh',
                'Exportaciones kWh': 'exports_kwh',
                'Importaciones kWh': 'imports_kwh'
            })
            
            # Convert date
            df['date'] = pd.to_datetime(df['date'])
            
            # Convert numeric columns
            numeric_cols = ['demand_kwh', 'generation_kwh', 'unserved_demand_kwh', 
                           'exports_kwh', 'imports_kwh']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove rows with NaN dates
            df = df.dropna(subset=['date'])
            
            print(f"  Loaded {len(df)} records from {Path(filepath).name}")
            return df
            
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None
    
    def load_all_files(self):
        """Load and merge all Excel files"""
        excel_files = glob.glob(str(self.raw_path / "*.xlsx"))
        
        if not excel_files:
            raise FileNotFoundError(f"No Excel files found in {self.raw_path}")
        
        all_data = []
        for file in excel_files:
            print(f"Loading {Path(file).name}...")
            df = self.load_excel_file(file)
            if df is not None and len(df) > 0:
                all_data.append(df)
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            combined = combined.drop_duplicates(subset=['date'], keep='first')
            combined = combined.sort_values('date').reset_index(drop=True)
            print(f"Total combined records: {len(combined)}")
            return combined
        else:
            raise ValueError("No data could be loaded")
    
    def clean_data(self, df):
        """Perform additional cleaning and feature engineering"""
        if len(df) == 0:
            return df
        
        data = df.copy()
        
        # Fill missing values
        numeric_cols = ['demand_kwh', 'generation_kwh', 'unserved_demand_kwh', 'exports_kwh', 'imports_kwh']
        for col in numeric_cols:
            if col in data.columns:
                data[col] = data[col].ffill().fillna(0)
        
        # Create time features
        data['day_of_week'] = data['date'].dt.dayofweek
        data['month'] = data['date'].dt.month
        data['day_of_year'] = data['date'].dt.dayofyear
        data['weekend'] = (data['day_of_week'] >= 5).astype(int)
        
        # Create lag features
        for lag in [1, 7, 14, 30]:
            data[f'demand_lag_{lag}'] = data['demand_kwh'].shift(lag)
        
        # Rolling averages
        for window in [7, 30]:
            data[f'demand_rolling_mean_{window}'] = data['demand_kwh'].rolling(window=window).mean()
        
        # Drop rows with NaN
        data = data.dropna(subset=['demand_lag_30'])
        
        print(f"After cleaning: {len(data)} records")
        return data
    
    def save_processed_data(self, df, filename="colombia_demand_2000_2024.csv"):
        """Save the processed dataset"""
        if len(df) == 0:
            return None
            
        output_path = self.processed_path / filename
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")
        return output_path
    
    def run_pipeline(self):
        """Execute the complete preprocessing pipeline"""
        print("=" * 50)
        print("Starting data preprocessing pipeline...")
        print("=" * 50)
        
        print("\n1. Loading raw Excel files...")
        data = self.load_all_files()
        
        if len(data) == 0:
            print("Error: No data loaded")
            return None
        
        print("\n2. Cleaning and feature engineering...")
        cleaned_data = self.clean_data(data)
        
        print("\n3. Saving processed data...")
        self.save_processed_data(cleaned_data)
        
        print("\n4. Data summary:")
        print(f"   Date range: {cleaned_data['date'].min()} to {cleaned_data['date'].max()}")
        print(f"   Total records: {len(cleaned_data)}")
        print(f"   Average demand: {cleaned_data['demand_kwh'].mean():,.0f} kWh")
        
        return cleaned_data


if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    data = preprocessor.run_pipeline()
    if data is not None:
        print("\n✓ Preprocessing complete!")