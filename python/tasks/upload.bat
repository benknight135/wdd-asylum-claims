@echo off

SET scriptpath=%~dp0

:: Upload to test pip
python -m twine upload --repository-url https://test.pypi.org/legacy/ %scriptpath%../dist/*
:: Upload to pip
python -m twine upload %scriptpath%../dist/*