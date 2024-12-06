python .\src\main.py
pip freeze
pip freeze > .\freeze.txt
mypy .\src\main.py
mypy .\src\main.py > .\mypy.txt