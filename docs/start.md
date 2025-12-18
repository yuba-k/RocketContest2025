# start.py

##  使用ライブラリ
-`logging`&nbsp;&nbsp;&nbsp;&nbsp;:pythonでのログ使用用ライブラリ<br>
-`time`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:pythonでの時間計測用ライブラリ<br>
-`RPi.GPIO`&nbsp;&nbsp;:pythonでraspberrypiを扱うためのライブラリ<br>
-`constants`:constants.pyで製作された独自ライブラリ

##  変数解説
1.`logger`
　　--このファイル専用のログファイルを取得<br>
2.`st_pin`
　　--PIN10番を使用(cansat.iniより)

##  関数解説
1.`def init()`<br>
  --任意のGPIOピンを出力（high）<br>
  2.`def awaiting()`<br>
  cansatの落下後の処理を司る。<br>
  --もし、value（出力）が０ならば、loggerにINFOメッセージとして「Start Program」と出力。<br>valueの値が1（出力）になるまで繰り返す。<br>処理後一秒待機する。パラシュート展開後の待機時間として30秒間待機する。

