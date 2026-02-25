import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
#from ultralytics import YOLO

import constants

######################################################
# 画像の取り扱い：BGR形式                              #
######################################################

_executor = ThreadPoolExecutor(max_workers=8)
#model = YOLO("../model/last_ncnn_model")

logger = logging.getLogger(__name__)


def binaryNoiseCutter(img):
    #    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    contours = [c for c in contours if cv2.contourArea(c) > 100]
    out = np.zeros_like(img)
    if not contours:
        return out
    cv2.drawContours(out, [max(contours, key=cv2.contourArea)], -1, 255, -1)
    return out


def opening(img):
    # gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # _, img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
    kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN,kernel, iterations = 3)
    # img = cv2.erode(img, kernel, iterations=3)
    # img = cv2.dilate(img, kernel, iterations=3)
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    contours = [c for c in contours if cv2.contourArea(c) > 1000]
    if not contours:
        return img
    out = np.zeros_like(img)
    cv2.drawContours(out, [max(contours, key=cv2.contourArea)], -1, 255, -1)
    return out


def red_mask(hsv):
    mask1 = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
    mask2 = cv2.inRange(hsv, (170, 100, 100), (180, 255, 255))
    mask = cv2.bitwise_or(mask1, mask2)
#    masked = cv2.bitwise_and(img, img, mask=mask)
    return opening(mask)


def split_by_size(img, size):
    rows = int(np.ceil(img.shape[0] / size[0]))
    cols = int(np.ceil(img.shape[1] / size[1]))
    return [
        chunk
        for row in np.array_split(img, rows, axis=0)
        for chunk in np.array_split(row, cols, axis=1)
    ]


def get_target_points2(binary, img):
    countors, _ = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS
    )
    if countors == ():
        cv2.putText(img, text = "there is not", org = (100,100), fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1, color = (0,0,0), thickness = 3)
        return "ERROR", img
    for c in countors:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return get_center_point(x + w, x), img


def get_center_point(right, left, top=None):
    if top is None:
        result = (right + left) // 2
    else:
        result = ((right + left) / 2 + top) // 2
    if (right - left) >= (constants.WIDTH * 0.6):
        return "goal"
    elif result < constants.WIDTH // 3:
        return "left"
    elif result < constants.WIDTH // 3 * 2:
        return "forward"
    else:
        return "right"


def get_coordinates(img):
    white_pixels = np.where(img == 255)
    return white_pixels


def merge_chunks(chunks, original_shape, size):
    """分割した画像チャンクを1枚に戻す"""
    h, w, c = original_shape
    row_size, col_size = size
    rows = int(np.ceil(h / row_size))
    cols = int(np.ceil(w / col_size))

    # 行ごとにまとめる
    merged_rows = []
    for r in range(rows):
        start = r * cols
        end = start + cols
        row_imgs = chunks[start:end]
        merged_row = np.concatenate(row_imgs, axis=1)
        merged_rows.append(merged_row)

    # 全体を縦に結合
    merged = np.concatenate(merged_rows, axis=0)
    # サイズを元にトリミング（分割時の端数ズレ対策）
    merged = merged[:h, :w]
    return merged


def imgprocess(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    chunk = (img.shape[0], img.shape[1] // 4)
    afImg = split_by_size(hsv, chunk)
    rsImg = list(_executor.map(red_mask, afImg))
    merge = merge_chunks(rsImg, img.shape, chunk)
    merge = binaryNoiseCutter(merge)
    result, rsimg = get_target_points2(merge, img)
    if result == "ERROR":
        return "search", rsimg
    else:
        return result, rsimg


def detect_objects_long_range(img):
    ret = model(img)
    x1, x2, y1, y2 = [int(i) for i in ret[0].boxes.xyxy[0]]
    return get_center_point(x1, x2)


def main():
    path = "../img/original"
    files = os.listdir(path)
    for fname in files:
        try:
            read_img = cv2.imread(os.path.join(path, fname))
            _, img = imgprocess(cv2.cvtColor(read_img, cv2.COLOR_BGR2RGB))
            cv2.imwrite(os.path.join("../img/result", fname), img)
        except KeyboardInterrupt:
            print("KeyboardInterrupt")


if __name__ == "__main__":
    main()
