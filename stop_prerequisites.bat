@echo off
rem Script description: WINDOWS ONLY. CLOSE THE RUNNING SERVERS AND PROGRAMS

cd /d G:\postgresql-18.4-1-windows-x64-binaries\pgsql\bin
pg_ctl -D "G:\postgresql-18.4-1-windows-x64-binaries\db" -l logfile stop

cd G:\Redis-8.6.3-Windows-x64-msys2
taskkill /IM redis-server.exe /F

cd G:\
taskkill /IM MailHog_windows_amd64.exe /F