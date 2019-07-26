# HOW TO BUILD

Check latest version of tools

```bash
python -m pip install --user --upgrade setuptools wheel
python -m pip install --user --upgrade twine
```

Build package

```bash
python setup.py sdist bdist_wheel
```

Upload package to test pip

```bash
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Install test pip

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps wddasylumclaims
```
