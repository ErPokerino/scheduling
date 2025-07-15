@echo off
REM Script per build e deployment dell'app Scheduling con Docker (Windows)
REM Uso: docker-build.bat [build|run|stop|clean|logs]

setlocal enabledelayedexpansion

REM Controlla se Docker è installato
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker non è installato. Installa Docker Desktop prima di continuare.
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose non è installato. Installa Docker Compose prima di continuare.
    exit /b 1
)

REM Controlla se il file .env esiste
if not exist ".env" (
    echo [WARNING] File .env non trovato. Creo un template...
    if exist "env.example" (
        copy env.example .env >nul
        echo [INFO] File .env creato da env.example
        echo [WARNING] Modifica il file .env con le tue configurazioni prima di continuare!
        pause
        exit /b 1
    ) else (
        echo [ERROR] File env.example non trovato. Crea manualmente il file .env
        pause
        exit /b 1
    )
)

REM Menu principale
if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="build" goto build
if "%1"=="run" goto run
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="clean" goto clean
if "%1"=="status" goto status
goto help

:build
echo [INFO] Building Docker image...
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Build fallito!
    pause
    exit /b 1
)
echo [SUCCESS] Build completato!
goto end

:run
echo [INFO] Avvio dell'applicazione...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Avvio fallito!
    pause
    exit /b 1
)
echo [SUCCESS] Applicazione avviata!
echo [INFO] Accesso disponibile su: http://localhost:8501
echo [INFO] Per vedere i log: docker-build.bat logs
goto end

:stop
echo [INFO] Fermando l'applicazione...
docker-compose down
echo [SUCCESS] Applicazione fermata!
goto end

:restart
echo [INFO] Riavvio dell'applicazione...
docker-compose down
timeout /t 2 /nobreak >nul
docker-compose up -d
echo [SUCCESS] Applicazione riavviata!
goto end

:logs
echo [INFO] Mostrando i log...
docker-compose logs -f
goto end

:clean
echo [WARNING] Pulizia completa - questo rimuoverà tutti i container e le immagini!
set /p confirm="Sei sicuro? (y/N): "
if /i "!confirm!"=="y" (
    echo [INFO] Rimozione container e immagini...
    docker-compose down --rmi all --volumes --remove-orphans
    echo [SUCCESS] Pulizia completata!
) else (
    echo [INFO] Pulizia annullata.
)
goto end

:status
echo [INFO] Stato dei container:
docker-compose ps
goto end

:help
echo Script per build e deployment dell'app Scheduling con Docker
echo.
echo Uso: %0 [comando]
echo.
echo Comandi disponibili:
echo   build    - Build dell'immagine Docker
echo   run      - Avvia l'applicazione
echo   stop     - Ferma l'applicazione
echo   restart  - Riavvia l'applicazione
echo   logs     - Mostra i log
echo   clean    - Pulisce tutto (container, immagini, volumi)
echo   status   - Mostra lo stato dei container
echo   help     - Mostra questo aiuto
echo.
echo Esempi:
echo   %0 build ^&^& %0 run    # Build e avvio
echo   %0 logs               # Visualizza log
echo   %0 stop               # Ferma l'app
echo.
goto end

:end
endlocal 