@echo off

cd C:
:: Install wddasylumclaims package
python -m pip install wddasylumclaims
:: Upgrade to make sure latest version is installed
python -m pip install --upgrade wddasylumclaims