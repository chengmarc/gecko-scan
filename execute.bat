@echo off

python -m venv __venv__
call __venv__\Scripts\activate.bat
pip install dependencies.tar.gz
echo.
echo Virtual environment setup completed.
pause

echo.
echo ##########################
echo ##### Execution No.1 #####
echo ##########################
echo.
call gecko_scan_all_crypto.py

echo.
echo ##########################
echo ##### Execution No.2 #####
echo ##########################
echo.
call gecko_scan_categories.py

echo.
echo Execution fully completed.
pause