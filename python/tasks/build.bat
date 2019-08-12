@echo off

:: Clean build directories
rmdir /S /Q dist
rmdir /S /Q build
rmdir /S /Q wddasylumclaims.egg-info

:: Build package
SET scriptpath=%~dp0
python %scriptpath%..\setup.py sdist bdist_wheel