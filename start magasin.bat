@echo off
setlocal

REM --------------------------------------------
REM Script pour demarrer NocoDB et attendre qu'il soit pret
REM --------------------------------------------

REM Verifie si NocoDB est deja en cours
tasklist /FI "IMAGENAME eq Noco-win-x64.exe" | find /I "Noco-win-x64.exe" >nul
IF %ERRORLEVEL%==0 (
    echo NocoDB est deja en cours.
) ELSE (
    echo Demarrage de NocoDB...
    cd /d "C:\FestiMagazDB"
    start "FestiMagazDB Server" ".\Noco-win-x64.exe"
)

REM Boucle d'attente jusqu'a ce que localhost:8080 reponde
set "maxWait=120"
set /a count=0

:wait_loop

timeout /t 1 >nul
curl -s http://localhost:8080 >nul 2>&1
if %ERRORLEVEL%==0 (
    echo NocoDB est pret !
    goto open_browser
)

set /a count+=1
if %count% GEQ %maxWait% (
    echo echec : NocoDB ne repond pas apres %maxWait% secondes.
    goto end
)
goto wait_loop

:open_browser
start http://localhost:8080

:end
endlocal
