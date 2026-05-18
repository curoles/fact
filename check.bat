@echo off
set SCRIPT_DIR=%~dp0
set ROOTS=%SCRIPT_DIR%kg,%SCRIPT_DIR%kg2,%SCRIPT_DIR%..\fact_physics,%SCRIPT_DIR%..\fact_math,%SCRIPT_DIR%..\fact_computer,%SCRIPT_DIR%..\fact_chemistry
python.exe %SCRIPT_DIR%pysrc\check.py --roots %ROOTS% --all %*
