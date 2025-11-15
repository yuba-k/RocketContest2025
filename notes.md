## 現在発生している問題点
+ モータ制御の遅延（認識はしているが，指令が遅れるため結果的にゴールへ到達できない）
+ binaryNoiseCutter関数でエラー．
```shell
Traceback (most recent call last):
  File "/usr/lib/python3.9/threading.py", line 954, in _bootstrap_inner
    self.run()
  File "/usr/lib/python3.9/threading.py", line 892, in run
    self._target(*self._args, **self._kwargs)
  File "/home/pi/RocketContest2025/src/MaineController.py", line 31, in appro
    cmd, _ = imgProcess.imgprocess(frame)
  File "/home/pi/RocketContest2025/src/imgProcess.py", line 123, in imgproces
    merge = binaryNoiseCutter(merge)
  File "/home/pi/RocketContest2025/src/imgProcess.py", line 16, in binaryNois
    cv2.drawContours(out, [max(contours, key=cv2.contourArea)], -1, 255, -1)
ValueError: max() arg is an empty sequence
```

## 実装予定
・画像処理の距離に応じた処理切替
    （長距離：Yolo等物体検出，中距離：リアルタイム色検出，近距離：小さいサイズでのリアルタイム色検出）