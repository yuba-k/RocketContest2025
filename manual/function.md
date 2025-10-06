# 実装する機能一覧
## 位置情報関連(coordinate_utils.py)
### __init__
位置情報モジュールの初期化
### connect
接続
### disconnect
切断
### parse_nmea_sentence
NMETA分を解析
### get_gps_data
位置情報データ取得
### calculate_target_distance_angle
目標地点までの距離と角度を算出
### cheak_data
取得したデータをフィルタリング

## カメラ関連(camera.py)
### __init__
カメラの初期化
### cap
カメラのフレーム取得
### save
フレームの保存
### disconnect
カメラの切断

## 画像処理(imgProcess.py)
### opening
モルフォロジー処理（ノイズ処理）
### red_mask
赤色検出
### split_by_size
画像を分割
### merge_chunks
画像を統合

## 6軸センサ関連(gyro_angle.py)
### __init__
センサ初期化
### getAngle
変化角算出

### モータ関連(motor.py)
## __init__
モータ設定初期化
## move
モータ動作
## cleanup
GPIO設定開放

## ログ書き込み(logwrite.py)
## __init__
ログの初期化
## wrote
ログ書き込み

## 設定ファイル読み込み(configload.py)
## __init__
読み込み初期化
## readConfig
設定ファイル読み込み