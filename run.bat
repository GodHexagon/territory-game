@echo off

:: インストールするパッケージをrequirements.txtからインストール
pip install -r .\requirements.txt

:: Pythonスクリプト実行時の標準出力とエラー出力をlog.txtに追記
echo ======= Running main.py ======= %DATE% %TIME% > .\log.txt
python -m src >> .\log.txt 2>&1

:: 改行を追加
echo. >> .\log.txt  

:: 現在のパッケージ一覧をlog.txtに保存（freeze部分）
echo ======= pip freeze ======= >> .\log.txt
pip freeze >> .\log.txt
