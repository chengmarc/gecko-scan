@echo off

echo Starting virtual environment setup.
echo.
python -m venv __venv__
call __venv__\Scripts\activate.bat
pip install dependencies\dist\gsl-dependencies-1.0.tar.gz
echo.
echo Virtual environment setup completed.
pause

echo.
echo ###########################
echo ##### Extract for all #####
echo ###########################
echo.
call core-process\gecko_scan_all_crypto.py

echo.
echo ###############################
echo ##### Extract by category #####
echo ###############################
echo.
call core-process\gecko_scan_categories.py

echo.
echo Execution fully completed.
pause