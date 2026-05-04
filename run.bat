@echo off
cd /d "%~dp0"
chcp 65001 >nul 2>&1

echo === Step 1: Check Python ===
where python 2>&1
python --version 2>&1

echo === Step 2: Test Import ===
python -u -c "print('Python works!')" 2>&1

echo === Step 3: Test sys.path ===
python -u -c "import sys; sys.path.insert(0, r'.'); print('Path OK'); from src.models import BattleState; print('Import OK')" 2>&1

echo === Step 4: Start Local Web Simulator ===
python run_web.py 2>&1

echo === All Done ===
pause
