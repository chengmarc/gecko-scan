@echo off
python --version
echo Starting virtual environment setup.
echo.
python -m venv __venv__
call __venv__\Scripts\activate.bat
pip install dependencies\dist\gsl-dependencies-1.3.tar.gz
echo.
echo Virtual environment setup completed.
echo.
call core-process\gecko_scan_gui.py