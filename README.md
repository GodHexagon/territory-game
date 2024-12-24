ライブラリ「pyxel」を用いて、ゲーム「ブロックス」をゲームアプリとして遊べることを目的とした、Pythonソースコードです。

pyxel: https://github.com/kitao/pyxel

ブロックス: https://mattel.co.jp/toys/mattel_games/mattel_games-11132/

## 遊び方

以下のどちらの方法でも、遊ぶことができます。

ビルドされた.exeファイルを実行する方法と、Python3インタプリンタを用いてスクリプトを実行する方法です。

### .exeファイルを実行する

以下のブランチに移動して、「Download ZIP」を用いてダウンロードします。

https://github.com/GodHexagon/territory-game/tree/dist/alpha/vsai-1-1

以下のように、「<> Code ▼」 -> 「Download ZIP」となっているはずです。

![image](https://github.com/user-attachments/assets/f815076d-25e4-4f16-942e-46c7011ef8a7)


ZIP形式でダウンロードされますので、解凍します。

中に入っている、`territory_game.exe`というファイルを実行すると、ゲームが起動します。

### Python3インタプリンタで実行する

この方法では、Python3インタプリンタが、環境にインストールされている必要があります。

当該リポジトリをローカルにクローンします。

masterブランチに移動します。

Windowsの場合は、リポジトリルートから、".\run.bat"の位置にあるファイルを実行すると、自動でゲームが起動します。

それ以外の場合でも、リポジトリルートから、以下のコマンドを実行することで、同様にゲームが起動するはずです（未検証）。

```
pip install -r ./requirements.txt
python ./src/main.py

```

## 使用技術

Python 3

pipライブラリ: numpy, pyxel, mypy, pyinstaller
