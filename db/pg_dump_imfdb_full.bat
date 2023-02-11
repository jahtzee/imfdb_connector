@echo off

REM Dump imfdb full

"pg_dump.lnk" -U imfdb imfdb > imfdb.sql

pause