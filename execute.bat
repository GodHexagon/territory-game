pip install -r .\requirements.txt
python .\src\main.py
pip freeze > .\freeze.txt
mypy .\src\main.py > .\mypy.txt