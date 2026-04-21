"""
api/main.py - FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Colombia Energy Demand Forecast API",
    description="API for forecasting energy demand in Colombia's National Interconnected System (SIN)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Colombia Energy Demand Forecast API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "historical": "/historical"
        }
    }

# Health endpoint
@app.get("/health")
async def health():
    from .services import get_prediction_service
    try:
        service = get_prediction_service()
        return {
            "status": "healthy",
            "model_loaded": service.model is not None,
            "data_available_until": service.get_last_year()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Predict endpoint
@app.get("/predict")
async def predict(days: int = 365):
    from .services import get_prediction_service
    
    if days < 1 or days > 730:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 730")
    
    try:
        service = get_prediction_service()
        
        if service.model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        predictions_df = service.predict(days=days)
        
        return {
            "status": "success",
            "year": int(predictions_df['date'].iloc[0][:4]),
            "total_days": len(predictions_df),
            "average_demand": float(predictions_df['predicted_demand_kwh'].mean()),
            "predictions": predictions_df.to_dict('records')
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Historical endpoint
@app.get("/historical")
async def historical(limit: int = 100):
    from .services import get_prediction_service
    
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 1000")
    
    try:
        service = get_prediction_service()
        
        if service.historical_data is None:
            raise HTTPException(status_code=503, detail="Historical data not loaded")
        
        data = service.historical_data.sort_values('date', ascending=False).head(limit)
        
        return {
            "status": "success",
            "total_records": len(service.historical_data),
            "data": data[['date', 'demand_kwh']].to_dict('records')
        }
    except Exception as e:
        logger.error(f"Historical error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)