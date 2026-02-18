# WeekFMEmitter.py

## 使用ライブラリ
-`logging`&nbsp;&nbsp;&nbsp;&nbsp;:pythonでのログ使用用ライブラリ<br>
-`time`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:pythonでの時間計測用ライブラリ<br>
-`RPi.GPIO`&nbsp;&nbsp;:pythonでraspberrypiを扱うためのライブラリ<br>
-`smbus`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:読み取り・書き取り等の通信を行う<br>
-`constants`:constants.pyで製作された独自ライブラリ

## 変数解説
1.`logger`
　　--このファイル専用のログファイルを取得<br>
## 関数解説
1.`def __init__(self)`
 --通信初期化・アドレス設定を行う。ここで、I2Cの1番ポートを開いている。`VOICE_SYNTH_ADDR` は 外部I2C機器のアドレスである。<br><br>
2.`def stringToAscii(self, message)`
 --文字をunicode,数を16進数に変換している。<br><br>
3.`def sendDataViaI2C(self, string)`
 --最後のコードをI2C経由で送信。最後に終了コードを送信。<br><br>
4.`def transmitFMMessage(self, message)`
 --以上の処理をまとめる