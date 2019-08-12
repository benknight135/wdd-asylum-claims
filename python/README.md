# Asulum Claims python package

## Required modules

- bs4
- requests
- pandas
- feather-format
- numpy
- argparse
- pypiwin32
- regex
- pyodbc

Install via pip

```bash
python -m pip wddasylumclaims
```

This will download all the required modules and install wddasylumclaims

## Run

Run script using:

```bash
python -m wddasylumclaims [optional arguments]
```

For help with optional arguments:

```bash
python -m wddasylumclaims -h
```
## Additional info

Also included with this package is a command line utility for converting between csv and feather files.
The is install automatically and is accessable from the command line.

Convert from feather to csv
```bash
convertfeather -i /path/to/input.feather -o /path/to/output.csv
```

Convert from csv to feather
```bash
converfeather -i /path/to/input.csv -o /path/to/output.feather
```
