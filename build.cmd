@echo off
setlocal enabledelayedexpansion
rem ---------------------------------------------------------------------------
rem FACTOR -- the whole build, and then the module gate.
rem
rem KICKOFF_M0.md Amendment 1: CMake with Ninja from the VS 2022 developer
rem environment, the preset, then `dumpbin /dependents` on factor.exe, which
rem fails if any of ws2_32, mswsock, winhttp, wininet, urlmon or dnsapi appears.
rem The gate is a lint and the header row says so; the fence is the sandbox.
rem
rem This is a batch file and not a one-liner because %errorlevel% inside
rem `cmd /c "..."` expands at parse time and lies. Every step prints its exit
rem code so a receipt can quote it.
rem
rem   build.cmd            configure, build, gate
rem   build.cmd clean      delete build\ first
rem ---------------------------------------------------------------------------

set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%
rem `cmake --build --preset` resolves the preset against the CURRENT directory,
rem not against -S, so the build must not depend on where it was called from.
cd /d "%ROOT%"
set PRESET=msvc-release
set BUILDDIR=%ROOT%\build
set VSDIR=C:\Program Files\Microsoft Visual Studio\2022\Community
set VCVARS=%VSDIR%\VC\Auxiliary\Build\vcvars64.bat
set VSCMAKE=%VSDIR%\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe
set VSNINJA=%VSDIR%\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja

if /i "%~1"=="clean" (
  if exist "%BUILDDIR%" rmdir /s /q "%BUILDDIR%"
  echo CLEANED %BUILDDIR%
)

if not exist "%VCVARS%" (
  echo BUILD_FAIL vcvars64.bat not found at "%VCVARS%"
  exit /b 9
)
call "%VCVARS%" >nul 2>&1
if errorlevel 1 (
  echo BUILD_FAIL VCVARS_FAILED
  exit /b 9
)

rem The VS-bundled CMake is the one Amendment 1 names; PATH may carry another.
if exist "%VSCMAKE%" (set CMAKE=%VSCMAKE%) else (set CMAKE=cmake)
if exist "%VSNINJA%" set PATH=%VSNINJA%;%PATH%

echo === toolchain ===
"%CMAKE%" --version | findstr /r /c:"^cmake version"
where ninja 2>nul | findstr /i ninja.exe
cl 2>&1 | findstr /r /c:"Version"

echo === configure ===
"%CMAKE%" --preset %PRESET% -S "%ROOT%"
set RC=%errorlevel%
echo CONFIGURE_EXIT=%RC%
if not "%RC%"=="0" (echo BUILD_FAIL configure & exit /b %RC%)

echo === build ===
"%CMAKE%" --build --preset %PRESET%
set RC=%errorlevel%
echo BUILD_EXIT=%RC%
if not "%RC%"=="0" (echo BUILD_FAIL build & exit /b %RC%)

set FACTOREXE=%BUILDDIR%\bin\factor.exe
if not exist "%FACTOREXE%" (
  echo BUILD_FAIL no binary at "%FACTOREXE%"
  exit /b 1
)

echo === module gate ===
rem Law 5 and law 10: the kernel links no network module. This is the lint half;
rem the OS refusal is F-EGRESS's, inside the launched sandbox.
dumpbin /nologo /dependents "%FACTOREXE%" > "%BUILDDIR%\dependents.txt" 2>&1
set RC=%errorlevel%
if not "%RC%"=="0" (echo BUILD_FAIL dumpbin exit %RC% & exit /b %RC%)
type "%BUILDDIR%\dependents.txt" | findstr /r /c:"\.dll"

findstr /i /c:"ws2_32" /c:"mswsock" /c:"winhttp" /c:"wininet" /c:"urlmon" /c:"dnsapi" "%BUILDDIR%\dependents.txt" >nul
if not errorlevel 1 (
  echo MODULE_GATE=FAIL -- a forbidden network module is linked:
  findstr /i /c:"ws2_32" /c:"mswsock" /c:"winhttp" /c:"wininet" /c:"urlmon" /c:"dnsapi" "%BUILDDIR%\dependents.txt"
  exit /b 1
)
echo MODULE_GATE=PASS -- none of ws2_32 mswsock winhttp wininet urlmon dnsapi

echo === selftest ===
"%FACTOREXE%" selftest
set RC=%errorlevel%
echo SELFTEST_EXIT=%RC%
if not "%RC%"=="0" (echo BUILD_FAIL selftest & exit /b %RC%)

echo BUILD_OK
exit /b 0
