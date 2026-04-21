"""
api/models.py - Pydantic models for API requests/responses
"""

from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional

class PredictionRequest(BaseModel):
    """Request model for prediction endpoint"""
    days: Optional[int] = Field(365, description="Number of days to predict", ge=1, le=730)
    include_history: Optional[bool] = Field(False, description="Include historical data in response")

class PredictionResponse(BaseModel):
    """Response model for single prediction"""
    date: date
    predicted_demand_kwh: float
    lower_bound_kwh: float
    upper_bound_kwh: float

class PredictionListResponse(BaseModel):
    """Response model for multiple predictions"""
    year: int
    total_days: int
    average_demand: float
    max_demand: float
    min_demand: float
    predictions: List[PredictionResponse]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    last_training_date: Optional[str]
    data_available_until: Optional[int]

class RetrainResponse(BaseModel):
    """Retrain model response"""
    status: str
    message: str
    training_date: Optional[str]
    records_used: int
    mae: Optional[float]
    rmse: Optional[float]