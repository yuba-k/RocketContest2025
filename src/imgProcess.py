from concurrent.futures import ThreadPoolExecutor
import cv2
import numpy as np
import time
import os

def opening(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    kernel = np.array([[0,1,0],[1,1,1],[0,1,0]], np.uint8)
    img = cv2.erode(img, kernel, iterations=3)
    img = cv2.dilate(img, kernel, iterations=3)
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    contours = [c for c in contours if cv2.contourArea(c) > 1000]
    if not contours:
        return img
    out = np.zeros_like(img)
    cv2.drawContours(out, [max(contours, key=cv2.contourArea)], -1, 255, -1)
    return out

def red_mask(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
    mask2 = cv2.inRange(hsv, (170, 100, 100), (180, 255, 255))
    mask = cv2.bitwise_or(mask1, mask2)
    masked = cv2.bitwise_and(img, img, mask=mask)
    return opening(masked)

def split_by_size(img, size):
    rows = int(np.ceil(img.shape[0] / size[0]))
    cols = int(np.ceil(img.shape[1] / size[1]))
    return [chunk for row in np.array_split(img, rows, axis=0)
                  for chunk in np.array_split(row, cols, axis=1)]


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

def main():
    path = "img/original/"
    files = os.listdir(path)
    for fname in files:
        img = cv2.imread(path+fname)
        chunk =  (img.shape[0] , img.shape[1] // 4 )
        afImg = split_by_size(img,chunk)

        st = time.time()
        with ThreadPoolExecutor(max_workers=8) as executor:
            rsImg = list(executor.map(red_mask, afImg))
        print(f"終了: {time.time() - st:.3f}秒")

        os.makedirs("img", exist_ok=True)
        for i, im in enumerate(rsImg):
            cv2.imwrite(f"img/chatgpt{i}.png", im)

        merge = merge_chunks(rsImg,img.shape,chunk)

        cv2.imwrite(f"img/result-{fname}.png",merge)

if __name__ == "__main__":
    main()

