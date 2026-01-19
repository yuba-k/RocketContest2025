# camera2.py
## 使用ライブラリ
-`logging`&nbsp;&nbsp;&nbsp;&nbsp;:pythonでのログ使用ライブラリ。<br>
-`threading`:pythonで並列処理を行いたい時に使用する標準ライブラリ。標準ライブラリなのでインストールの必要はない。構文等は下記URLを参照。<br>
[https://docs.python.org/ja/3.13/library/threading.html]
<br>-`enum`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:関連する定数をまとめて管理する列挙型（意味ある名前付き定数の集合を定義する）ライブラリ。
構文等は下記URLを参照。
[https://docs.python.org/ja/3/library/enum.html]
<br>-`cv2`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:画像・動画に様々な処理（画像処理等）を提供するライブラリ。<br>
-`numpy`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:pythonでより高度な演算を行いたい時に使用するライブラリ<br>
-`libcamera`:RaspberryPiでのカメラ使用時に使用。<br>
-`picamera2`:`libcamera`を使用する為にに使用。

## 変数解説
-`logger`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:このファイル専用のログファイルを取得
### Cameraクラス内の変数
-`self.picam`:raspberryPiのカメラ制御を行う。(以下は更に属性がついた場合の解説)
```python
self.picam.configure(...)     :設定
self.picam.set_controls(...)  :制御
self.picam.start()            :撮影開始
self.picam.capture_array()    :画像処理
self.picam.stop()             :停止
self.picam.close()            :解放
```

## 関数
※classに関してはgpsnew.mdで解説を行ったので省略する。
#### `def cap(self, cnt)`
カメラから画像を取得し、画像を様々な角度から調査し、画像を保存する。
#### `save(self, im, fullpath, mode)`
画像を指定した色で保存（RGB）
#### `disconnect(self)`
カメラの使用を終了し、リソースを解放する。
