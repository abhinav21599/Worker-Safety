@echo off
echo ========================================================
echo Starting AI-Powered Multi-PPE Safety Monitoring Dashboard
echo ========================================================
echo.
echo Please wait while Streamlit launches your browser...
echo.

:: Check if virtual environment exists, if so use it
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

:: Run the Streamlit application
streamlit run app.py

pause
