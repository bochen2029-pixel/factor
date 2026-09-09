@echo off
setlocal
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul || (echo VCVARS-FAIL & exit /b 1)
cd /d C:\FACTOR\probe\bin || exit /b 1

echo === compiling probe.exe ===
cl /nologo /std:c++17 /MT /O2 /W3 /EHsc /Fo:probe.obj /Fe:probe.exe C:\FACTOR\probe\src\probe.cpp ws2_32.lib advapi32.lib
if errorlevel 1 (echo PROBE-BUILD-FAIL & exit /b 1)

echo === compiling launcher.exe ===
cl /nologo /std:c++17 /MT /O2 /W3 /EHsc /Fo:launcher.obj /Fe:launcher.exe C:\FACTOR\probe\src\launcher.cpp userenv.lib advapi32.lib
if errorlevel 1 (echo LAUNCHER-BUILD-FAIL & exit /b 1)

echo BUILD-OK
exit /b 0
