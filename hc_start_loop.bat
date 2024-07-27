@echo off
echo Activating virtual environment...
call Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b
)
echo Virtual environment activated successfully.
echo Running python script...
python app/test_loop.py
