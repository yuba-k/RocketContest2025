# gpsnew.py

## 使用ライブラリ
<br>-`logging`&nbsp;&nbsp;&nbsp;&nbsp;:pythonでのログ使用用ライブラリ。<br>

-`math`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:複素数以外の数学処理を行える。複素数を扱いたい場合は`cmath`ライブラリを使用。詳しくは下記URLを参照。
<br>[https://docs.python.org/ja/3/library/math.html]
<br>

-`typing`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:pythonの型を判別するためのライブラリ。<br>*<基本形>*
```python
def add(a: int, b: int) -> int:
    return a + b
```
(解説)<br>
`a: int`:aはint型<br>
`-> int`:戻り値(関数を実行した後に呼び出し元へ戻す処理)は int 型<br>
詳しくは以下のURLを参照
<br>[https://docs.python.org/ja/3.10/library/typing.html]
(python公式ライブラリ)<br><br>
*<OptionalとTupleについて>*
<br>-`optional`:None を返す／受け取る可能性があることを明示する
<br>-`Turple`&nbsp;&nbsp;&nbsp;&nbsp;:順番・個数・型を固定できる
<br>-`serial`&nbsp;&nbsp;&nbsp;&nbsp;:データを1ビットずつ直列（シリアル）に、1本の信号線を使って順番に送受信する通信方式をraspberry piで利用するためのライブラリ。

## 変数解説
### GPSModuleクラスの変数
-`logger`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:このファイル専用のログファイルを取得<br>
-`self.port`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:通信するシリアルポート名（番号）<br>
-`self.baud_rate`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:通信速度<br>
-`self.serial_connection`:接続機名<br>
### connect / disconnect の変数
-`self.serial_connection`:GPSと通信する変数<br>
-`e`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:例外処理
### parse_nmea_sentence内の変数
-`sentence`:NMEA（標準通信規格）文<br>
-`parts`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:カンマの分割表示<br>
-`raw_lat`&nbsp;&nbsp;:生緯度<br>
-`raw_lon`&nbsp;&nbsp;:生経度<br>
-`lat_dir`&nbsp;&nbsp;:N(north)/S(south)<br>
-`lon_dir`&nbsp;&nbsp;:E(easte)/W(west)<br>
### get_gps_data内の変数
-`current_coordinate`&nbsp;&nbsp;:現在位置<br>
-`previous_coordinate`:直前位置<br>
-`goal_coordinate`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:目標位置<br>
-`TARGET_DISTANCE`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:到達判定距離<br>
### メインプログラム内の変数
-`lat`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:緯度<br>
-`lon`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:経度<br>
-`satellites`:衛星数<br>
-`utc_time`&nbsp;&nbsp;&nbsp;&nbsp;:時刻<br>
-`dop`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:精度<br>
## 関数・コード解説 
#### クラス
データ（変数）と処理（関数）をひとまとめにしたプログラムの事。
<br>EX）
```python
class Dog:
    pass
pochi = Dog()
```
`class`だけでは意味を為さないが、`pochi=Dog()`というインスタンス（値）を持たせることでデータの保持/変更/使用 が行える。

#### 関数
##### `connect(self):`
GPSとの通信を行う関数
##### `disconnect`
GPSとの通信を終了する関数
##### `parse_nmea_sentence`
NMEA文からGPS情報を読み取る関数。無効なデータは全てNONEを返す
##### `get_gps_data`
sirial から情報を読み取り、parse_nmea_sentence()に値を渡す
##### `calculate_target_distance_angle`
現在位置・進行方向・目標位置から 距離/進行方向 を計算し求める
##### `cheak_data`
GPSとの 経度/緯度/前回位置との差 が異常じゃないかを調べる