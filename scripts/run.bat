@echo off

cd ../
if exist "venv\" (
    call venv\Scripts\activate && echo venv activated
)
python main.py -le

pause
