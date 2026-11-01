@echo off
rem Builds SmartFood.exe with the C# compiler included in Windows (.NET Framework 4).
cd /d "%~dp0"
set CSC=%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe
if not exist "%CSC%" set CSC=%WINDIR%\Microsoft.NET\Framework\v4.0.30319\csc.exe
if not exist "%CSC%" (
  echo C# compiler not found.
  exit /b 1
)
if not exist "..\assets\smartfood.ico" powershell -NoProfile -ExecutionPolicy Bypass -File make_icon.ps1
"%CSC%" /nologo /target:winexe /optimize+ /win32icon:..\assets\smartfood.ico ^
  /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /out:..\SmartFood.exe SmartFood.cs || exit /b 1
echo Built SmartFood.exe
