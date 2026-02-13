# GPS関連
```shell
ls -l /dev/serial0
```
理想的な出力
```shell
/dev/serial0 -> ttyAMA0
```
こうなっていない場合
```shell
sudo vim /boot/config.txt
```
で`boot/config.txt`に`dtoverlay=disable-bt`を追記
```shell
ls -l /dev/serial0
```
を再度実行し，理想的な出力になることを確認

NMEA文をstdoutに出力させる
```shell
sudo minicom -b 9600 -D /dev/serial0
```