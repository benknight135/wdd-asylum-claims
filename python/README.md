# Asulum Claims for WDD Hackathon

## Required modules

- bs4
- requests
- pandas
- feather-format
- numpy

Install via pip
(Not currently released so using TestPyPi)

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps wddasylumclaims
```

## Run

Run script using:

```bash
python -m wddasylumclaims [optional arguments]
```

Arguments:

-f --filepath PATH_TO_CSV

(PATH_TO_CSV can also be the public web url to a google sheet)

-u --url URL_TO_SCRAPE
