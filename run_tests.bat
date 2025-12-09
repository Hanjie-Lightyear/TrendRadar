@echo off
REM Windows 测试运行脚本

echo Checking dependencies...
python -c "import rapidfuzz" 2>nul
if errorlevel 1 (
    echo Installing rapidfuzz...
    pip install rapidfuzz>=3.0.0,<4.0.0
)

python -c "import pytest" 2>nul
if errorlevel 1 (
    echo Installing pytest...
    pip install pytest>=7.0.0,<8.0.0
)

echo Running tests...
python -m pytest tests/ -v --tb=short

echo Tests completed!
