@echo off
rem Script description: WINDOWS ONLY. CHANGE THE DIRECTORIES AS NEEDED


@REM cd /d G:\postgresql-18.4-1-windows-x64-binaries\pgsql\bin
cd /d I:\postgresql-18.1-2-windows-x64-binaries\pgsql\bin
@REM pg_ctl -D "G:\postgresql-18.4-1-windows-x64-binaries\db" -l logfile start
pg_ctl -D "I:\postgresql-18.1-2-windows-x64-binaries\data" -l logfile start

@REM cd G:\Redis-8.6.3-Windows-x64-msys2
cd I:\Redis-x64-5.0.14
start "" redis-server.exe

@REM cd G:\
cd I:\
start "" MailHog_windows_amd64.exe

setlocal
cd /d "%~dp0"

FOR /F "usebackq eol=# tokens=* delims=" %%I IN ("%~dp0.env") DO (
  REM optional: skip empty lines
  if not "%%I"=="" SET %%I
)

REM Confirm
echo POSTGRES_DB=%POSTGRES_DB%
echo POSTGRES_USER=%POSTGRES_USER%
echo POSTGRES_HOST=%POSTGRES_HOST%
echo POSTGRES_PASSWORD=%POSTGRES_PASSWORD%
echo STRIPE_SECRET_KEY=%STRIPE_SECRET_KEY%
echo STRIPE_PUBLISHABLE_KEY=%STRIPE_PUBLISHABLE_KEY%
echo STRIPE_WEBHOOK_SECRET=%STRIPE_WEBHOOK_SECRET%
echo CELERY_BROKER_URL=%CELERY_BROKER_URL%

if "%~1"=="" (
  python manage.py runserver
) else (
  %~1
)

call "%~dp0stop_prerequisites.bat"

