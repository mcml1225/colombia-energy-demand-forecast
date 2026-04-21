"""
api/services.py - Business logic for predictions
"""

import pandas as pd
import pickle
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemandPredictionService:
    """Service for energy demand predictions"""
    
    def __init__(self, model_path: str = "models/prophet_model.pkl", 
                 data_path: str = "data/processed/colombia_demand_2000_2024.csv"):
        self.model_path = Path(model_path)
        self.data_path = Path(data_path)
        self.model = None
        self.historical_data = None
        self.load_model()
        self.load_historical_data()
        
    def load_model(self) -> bool:
        """Load trained model from disk"""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Model loaded from {self.model_path}")
                return True
            else:
                logger.warning(f"Model not found at {self.model_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def load_historical_data(self) -> bool:
        """Load historical data"""
        try:
            if self.data_path.exists():
                self.historical_data = pd.read_csv(self.data_path)
                self.historical_data['date'] = pd.to_datetime(self.historical_data['date'])
                logger.info(f"Historical data loaded: {len(self.historical_data)} records")
                return True
            else:
                logger.warning(f"Data not found at {self.data_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def get_last_year(self) -> int:
        """Get last year from historical data"""
        if self.historical_data is not None and len(self.historical_data) > 0:
            return self.historical_data['date'].max().year
        return None
    
    def predict(self, days: int = 365) -> pd.DataFrame:
        """Generate predictions for next year"""
        if self.model is None:
            raise ValueError("Model not available")
        
        last_year = self.get_last_year()
        if last_year is None:
            raise ValueError("No historical data available")
        
        # Create future dates starting from January 1st of next year
        next_year = last_year + 1
        start_date = pd.Timestamp(f'{next_year}-01-01')
        future_dates = pd.date_range(start=start_date, periods=days, freq='D')
        
        # Create future dataframe for Prophet
        future = pd.DataFrame({'ds': future_dates})
        
        # Generate forecast
        forecast = self.model.predict(future)
        
        # Extract results - convert to string dates for JSON serialization
        predictions = pd.DataFrame({
            'date': forecast['ds'].dt.strftime('%Y-%m-%d'),
            'predicted_demand_kwh': round(forecast['yhat'], 2)
        })
        
        return predictions

# Singleton instance
_prediction_service = None

def get_prediction_service() -> DemandPredictionService:
    """Get singleton instance of prediction service"""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = DemandPredictionService()
    return _prediction_service