@echo off
rem Script description: WINDOWS ONLY. CLOSE THE RUNNING SERVERS AND PROGRAMS

cd /d I:\postgresql-18.1-2-windows-x64-binaries\pgsql\bin
pg_ctl -D "I:\postgresql-18.1-2-windows-x64-binaries\data" -l logfile stop

cd I:\Redis-x64-5.0.14
taskkill /IM redis-server.exe /F

cd I:\
taskkill /IM MailHog_windows_amd64.exe /F