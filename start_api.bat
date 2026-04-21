@echo off
echo ========================================
echo Starting Energy Demand Forecast API
echo ========================================
echo.

call venv\Scripts\activate

echo Installing API dependencies...
pip install -r requirements-api.txt

echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo.

python -m api.main

pause