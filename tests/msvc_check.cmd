@echo off
setlocal
rem FACTOR tests: compile and run layout_check.cpp with MSVC, clean and planted lie.
rem Usage: msvc_check.cmd [outdir]   (default: %TEMP%\factor_layout)
set OUT=%~1
if "%OUT%"=="" set OUT=%TEMP%\factor_layout
if not exist "%OUT%" mkdir "%OUT%"
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
if errorlevel 1 (echo VCVARS_FAILED & exit /b 9)
cd /d "%OUT%"
cl /nologo /std:c++20 /EHsc /W4 "%~dp0layout_check.cpp" /Fe:layout_check.exe /Fo:layout_check.obj >cl_clean.log 2>&1
set CL_CLEAN=%errorlevel%
echo CL_CLEAN_EXIT=%CL_CLEAN%
if %CL_CLEAN% neq 0 type cl_clean.log
if not exist "%OUT%\layout_check.exe" (
  echo NO_EXE_PRODUCED
  goto lie
)
"%OUT%\layout_check.exe"
echo RUN_EXIT=%errorlevel%
:lie
cl /nologo /std:c++20 /EHsc /W4 /DPROVE_SPEC_FAILS "%~dp0layout_check.cpp" /Fe:layout_lie.exe /Fo:layout_lie.obj >cl_lie.log 2>&1
set CL_LIE=%errorlevel%
echo CL_LIE_EXIT=%CL_LIE%
findstr /c:"C2338" cl_lie.log >nul && echo LIE_REFUSED_C2338
if exist layout_lie.exe (echo LIE_BINARY_PRODUCED_BAD) else (echo LIE_NO_BINARY_GOOD)
endlocal
