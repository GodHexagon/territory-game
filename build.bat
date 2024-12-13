pip install -r .\requirements.txt
pyinstaller .\territory_game.spec
pip freeze > .\freeze.txt