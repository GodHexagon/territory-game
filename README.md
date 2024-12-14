ライブラリ「pyxel」を用いて、ゲーム「ブロックス」をゲームアプリとして遊べることを目的とした、Pythonソースコードです。

pyxel: https://github.com/kitao/pyxel

ブロックス: https://mattel.co.jp/toys/mattel_games/mattel_games-11132/

## 遊び方

以下のどちらの方法でも、遊ぶことができます。

ビルドされた.exeファイルを実行する方法と、Python3インタプリンタを用いてスクリプトを実行する方法です。

### .exeファイルを実行する

この方法では、PCのセキュリティが反応して.exeファイルを危険だと判断するようです。責任は負いかねますが、マルウェアが入っているわけではありません。無視してファイルを実行することでゲームを遊べます。

以下に示したファイルをダウンロードします。

https://github.com/GodHexagon/territory-game/blob/dist/alpha/vsai-1-0/territory_game.exe

これを実行すると、ゲームが起動します。

### Python3インタプリンタで実行する

この方法では、Python3インタプリンタが、環境にインストールされている必要があります。

当該リポジトリをローカルにクローンします。

Windowsの場合は、リポジトリルートから、".\run.bat"の位置にあるファイルを実行すると、自動でゲームが起動します。

それ以外の場合でも、リポジトリルートから、以下のコマンドを実行することで、同様にゲームが起動します。

```
pip install -r ./requirements.txt
python ./src/main.py

```

## 使用技術

Python 3

pipライブラリ: numpy, pyxel, mypy, pyinstaller
