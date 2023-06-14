# PIP packaging instructions
TL;DR;

```bash
pip install --upgrade pip
python3 -m pip install --user --upgrade setuptools wheel twine
python3 setup.py sdist bdist_wheel
python3 -m pip install -r requirements.txt --user
python3 -m twine upload dist/*

```

Full:
```bash
 python3 setup.py sdist bdist_wheel && python3 -m twine upload dist/*
 
```

in virtual env:
```bash
pip install --upgrade pip
pip install --upgrade setuptools wheel twine

#if bug with setuptools
pip install --upgrade --force-reinstall setuptools

python setup.py sdist bdist_wheel
python -m twine upload dist/*

#FULL:

python setup.py sdist bdist_wheel && python -m twine upload dist/*


python -m twine upload --cert ~/JLabCA.cer dist/*

```

JLAB CERTIFICATE ERROR:

```bash
python -m twine upload --cert /home/romanov/JLabCA.crt dist/*
```


A tutorial:
https://packaging.python.org/tutorials/packaging-projects/

edpm pip: https://pypi.org/project/edpm/#history

SO question for JLab certificate validation
https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror/10668173


