@echo off

REM Dump imfdb structure

"pg_dump.lnk" --schema-only -U imfdb imfdb > imfdb_structure.sql

pause