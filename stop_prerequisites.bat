@echo off
rem Script description: WINDOWS ONLY. CLOSE THE RUNNING SERVERS AND PROGRAMS

@REM cd /d G:\postgresql-18.4-1-windows-x64-binaries\pgsql\bin
cd /d I:\postgresql-18.1-2-windows-x64-binaries\pgsql\bin
@REM pg_ctl -D "G:\postgresql-18.4-1-windows-x64-binaries\db" -l logfile stop
pg_ctl -D "I:\postgresql-18.1-2-windows-x64-binaries\data" -l logfile stop

@REM cd G:\Redis-8.6.3-Windows-x64-msys2
cd I:\Redis-x64-5.0.14
taskkill /IM redis-server.exe /F

@REM cd G:\
cd I:\
taskkill /IM MailHog_windows_amd64.exe /F