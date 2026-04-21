"""
train_model.py - Time series forecasting using Prophet
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from pathlib import Path
import pickle
from sklearn.metrics import mean_absolute_error, mean_squared_error
import yaml

class DemandForecaster:
    """
    Time series forecasting for energy demand using Facebook Prophet
    """
    
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.model = None
        
    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        default_config = {
            'model': {
                'changepoint_prior_scale': 0.05,
                'seasonality_prior_scale': 10.0,
                'yearly_seasonality': True,
                'weekly_seasonality': True,
                'daily_seasonality': False,
                'seasonality_mode': 'additive'
            },
            'forecast': {
                'periods': 365,
                'freq': 'D'
            }
        }
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            return default_config
    
    def prepare_data(self, df, target_col='demand_kwh'):
        """Prepare data for Prophet (needs ds and y columns)"""
        prophet_df = df[['date', target_col]].copy()
        prophet_df = prophet_df.rename(columns={'date': 'ds', target_col: 'y'})
        
        # Remove any NaN or infinite values
        prophet_df = prophet_df.dropna()
        prophet_df = prophet_df[np.isfinite(prophet_df['y'])]
        
        return prophet_df
    
    def train(self, data, test_size=365):
        """
        Train Prophet model on historical data
        
        Args:
            data: DataFrame with 'date' and 'demand_kwh' columns
            test_size: Number of days to hold out for testing
        """
        # Prepare data
        prophet_df = self.prepare_data(data)
        
        # Split train/test (last test_size days for testing)
        if len(prophet_df) > test_size:
            train_df = prophet_df.iloc[:-test_size]
            test_df = prophet_df.iloc[-test_size:]
        else:
            train_df = prophet_df
            test_df = None
            print(f"Warning: Only {len(prophet_df)} days of data, skipping test set")
        
        # Initialize Prophet model
        self.model = Prophet(
            changepoint_prior_scale=self.config['model']['changepoint_prior_scale'],
            seasonality_prior_scale=self.config['model']['seasonality_prior_scale'],
            yearly_seasonality=self.config['model']['yearly_seasonality'],
            weekly_seasonality=self.config['model']['weekly_seasonality'],
            daily_seasonality=self.config['model']['daily_seasonality'],
            seasonality_mode=self.config['model']['seasonality_mode']
        )
        
        # Train the model
        print("Training Prophet model...")
        self.model.fit(train_df)
        
        # Evaluate on test set if available
        if test_df is not None and len(test_df) > 0:
            forecast = self.model.predict(test_df[['ds']])
            metrics = self.evaluate(test_df['y'], forecast['yhat'])
            print(f"\nTest set metrics:")
            print(f"  MAE: {metrics['mae']:,.0f} kWh")
            print(f"  RMSE: {metrics['rmse']:,.0f} kWh")
            print(f"  MAPE: {metrics['mape']:.2f}%")
        
        return self.model
    
    def predict(self, periods=None, last_date=None):
        """
        Generate future predictions starting from the year after last data point
        
        Args:
            periods: Number of days to predict (default: 365)
            last_date: Last date from historical data (auto-detected if not provided)
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        periods = periods or self.config['forecast']['periods']
        
        # Create future dates starting from next year
        if last_date:
            # Start from January 1st of next year
            next_year = last_date.year + 1
            start_date = pd.Timestamp(f'{next_year}-01-01')
            future_dates = pd.date_range(start=start_date, periods=periods, freq='D')
        else:
            # Fallback: use current date
            start_date = pd.Timestamp.now() + pd.DateOffset(days=1)
            future_dates = pd.date_range(start=start_date, periods=periods, freq='D')
        
        # Create future dataframe for Prophet
        future = pd.DataFrame({'ds': future_dates})
        
        # Generate forecast
        forecast = self.model.predict(future)
        
        # Extract relevant columns
        predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        predictions = predictions.rename(columns={
            'ds': 'date',
            'yhat': 'predicted_demand_kwh',
            'yhat_lower': 'lower_bound_kwh',
            'yhat_upper': 'upper_bound_kwh'
        })
        
        return predictions
    
    def evaluate(self, y_true, y_pred):
        """Calculate evaluation metrics"""
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape
        }
    
    def save_model(self, path="models/prophet_model.pkl"):
        """Save trained model to disk"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"Model saved to {path}")
    
    def load_model(self, path="models/prophet_model.pkl"):
        """Load trained model from disk"""
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
        print(f"Model loaded from {path}")


if __name__ == "__main__":
    print("DemandForecaster class available for import")