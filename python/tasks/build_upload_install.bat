@echo off

SET scriptpath=%~dp0

:: Run build script
call %scriptpath%\build.bat

:: Run upload script
call %scriptpath%\upload.bat

:: Run install script
call %scriptpath%\install.bat