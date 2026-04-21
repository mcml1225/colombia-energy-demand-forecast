"""
api/routes.py - API endpoints
"""

from fastapi import APIRouter, HTTPException
import logging

from .models import (
    PredictionRequest, 
    PredictionListResponse, 
    PredictionResponse,
    HealthResponse
)
from .services import get_prediction_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", tags=["root"])
async def router_root():
    """Router root endpoint"""
    return {
        "message": "API v1 - Colombia Energy Demand Forecast",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/v1/health",
            "predict": "/api/v1/predict",
            "predict_year": "/api/v1/predict/{year}",
            "historical": "/api/v1/historical"
        }
    }

@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint"""
    service = get_prediction_service()
    last_year = service.get_last_year()
    
    return HealthResponse(
        status="healthy",
        model_loaded=service.model is not None,
        last_training_date=service.last_training_date.isoformat() if service.last_training_date else None,
        data_available_until=last_year
    )

@router.post("/predict", response_model=PredictionListResponse, tags=["predictions"])
async def predict(request: PredictionRequest):
    """Generate predictions for next year"""
    try:
        service = get_prediction_service()
        
        if service.model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Generate predictions
        predictions_df = service.predict(days=request.days)
        summary = service.get_prediction_summary(predictions_df)
        
        # Convert to response format
        predictions_list = []
        for _, row in predictions_df.iterrows():
            predictions_list.append(PredictionResponse(
                date=row['date'].date(),
                predicted_demand_kwh=round(row['predicted_demand_kwh'], 2),
                lower_bound_kwh=round(row['lower_bound_kwh'], 2),
                upper_bound_kwh=round(row['upper_bound_kwh'], 2)
            ))
        
        return PredictionListResponse(
            year=summary['year'],
            total_days=summary['total_days'],
            average_demand=round(summary['average_demand'], 2),
            max_demand=round(summary['max_demand'], 2),
            min_demand=round(summary['min_demand'], 2),
            predictions=predictions_list
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predict/{year}", response_model=PredictionListResponse, tags=["predictions"])
async def predict_by_year(year: int):
    """Get predictions for a specific year (must be future year)"""
    try:
        service = get_prediction_service()
        
        if service.model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        last_year = service.get_last_year()
        
        if year <= last_year:
            raise HTTPException(
                status_code=400, 
                detail=f"Year {year} is in the past. Last available data is {last_year}"
            )
        
        # Generate predictions
        days_in_year = 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365
        predictions_df = service.predict(days=days_in_year)
        
        # Filter for requested year
        predictions_df = predictions_df[predictions_df['date'].dt.year == year]
        
        if len(predictions_df) == 0:
            raise HTTPException(status_code=404, detail=f"No predictions available for {year}")
        
        predictions_list = [
            PredictionResponse(
                date=row['date'].date(),
                predicted_demand_kwh=round(row['predicted_demand_kwh'], 2),
                lower_bound_kwh=round(row['lower_bound_kwh'], 2),
                upper_bound_kwh=round(row['upper_bound_kwh'], 2)
            )
            for _, row in predictions_df.iterrows()
        ]
        
        return PredictionListResponse(
            year=year,
            total_days=len(predictions_df),
            average_demand=round(predictions_df['predicted_demand_kwh'].mean(), 2),
            max_demand=round(predictions_df['predicted_demand_kwh'].max(), 2),
            min_demand=round(predictions_df['predicted_demand_kwh'].min(), 2),
            predictions=predictions_list
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical", tags=["data"])
async def get_historical_data(limit: int = 100, offset: int = 0):
    """Get historical demand data"""
    service = get_prediction_service()
    
    if service.historical_data is None:
        raise HTTPException(status_code=503, detail="Historical data not loaded")
    
    data = service.historical_data.sort_values('date', ascending=False)
    data = data.iloc[offset:offset + limit]
    
    return {
        "total_records": len(service.historical_data),
        "limit": limit,
        "offset": offset,
        "data": data[['date', 'demand_kwh', 'generation_kwh']].to_dict('records')
    }