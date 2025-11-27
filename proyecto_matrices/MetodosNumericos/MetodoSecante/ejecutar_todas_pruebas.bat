@echo off
chcp 65001 >nul
echo ================================================================================
echo  EJECUTANDO TODAS LAS PRUEBAS - MÉTODO DE LA SECANTE
echo ================================================================================
echo.

echo [1/2] Ejecutando Pruebas Exhaustivas (30 casos)...
echo --------------------------------------------------------------------------------
python test_exhaustivo.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Las pruebas exhaustivas fallaron
    pause
    exit /b 1
)

echo.
echo.
echo [2/2] Ejecutando Pruebas Complementarias (15 casos)...
echo --------------------------------------------------------------------------------
python test_botones_faltantes.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Las pruebas complementarias fallaron
    pause
    exit /b 1
)

echo.
echo.
echo ================================================================================
echo  TODAS LAS PRUEBAS COMPLETADAS
echo ================================================================================
echo.
echo Total de casos ejecutados: 45
echo.
echo Archivos de resultados generados:
echo   - RESULTADOS_PRUEBAS.md
echo   - RESUMEN_FINAL_PRUEBAS.md
echo.
echo Para ver los resultados detallados, abre los archivos .md
echo.
pause
