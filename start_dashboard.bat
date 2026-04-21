@echo off
echo ========================================
echo Starting Energy Demand Dashboard
echo ========================================
echo.

call venv\Scripts\activate

echo Installing Streamlit...
pip install streamlit plotly

echo.
echo Starting dashboard...
echo Dashboard will open in your browser
echo.

streamlit run dashboard.py

pause