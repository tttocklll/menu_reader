import cv2
import pyocr
import sys
import os
from PIL import Image
import shutil
import subprocess
import numpy as np


def onMouse(e, x, y, flag, params):
    global ratio
    if e == cv2.EVENT_MOUSEWHEEL:
        if flag > 0:
            ratio += 0.1
        else:
            ratio -= 0.1
        if ratio <= 0:
            ratio = 0.1
        ratio = float('{:.1f}'.format(ratio))



def cv2pil(image):
    new_image = image.copy()
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
    new_image = Image.fromarray(new_image)
    return new_image


def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None


def main():
    cap = cv2.VideoCapture(0)
    lang = "eng"
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        sys.exit(1)
    tool = tools[0]

    if os.path.isdir("img"):
        shutil.rmtree("img")
    os.mkdir("img")
    searched = []
    while cap.isOpened():
        r, frame = cap.read()
        if not r:
            break
        cv2.imshow("src", frame)
        # OpenCVでの加工
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("gray", gray)
        _, thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_OTSU)
        cv2.imshow("thresh", thresh)
        # OCR
        img_pil = cv2pil(thresh)
        res = tool.image_to_string(img_pil,
                                   lang=lang,
                                   builder=pyocr.builders.LineBoxBuilder())
        im = thresh.copy()
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        for d in res:
            keyword = d.content.replace(" ", "_") if lang == "eng" else d.content.replace(" ", "")
            cv2.rectangle(im, d.position[0], d.position[1], (0, 0, 255), 2)
            if keyword and keyword in searched:  # すでに画像があったら貼り付け
                try:
                    tmp = imread(f"img/{keyword}.png")
                    tmp = cv2.resize(tmp, None, None, ratio, ratio)
                    frame[d.position[0][1]:d.position[0][1]+tmp.shape[0],
                          d.position[1][0]:d.position[1][0]+tmp.shape[1]] = tmp
                except Exception as e:
                    print(keyword, e)
            else:  # なかったら検索してくる
                subprocess.Popen(f"python scraper.py {d.content if lang == 'eng' else keyword}",
                                 cwd="D:/Users/tocky/Documents/exp_3A/OpenCV_GL/last", shell=True)
                searched.append(keyword)
        cv2.imshow("words", im)

        cv2.putText(frame, f"lang = {lang}, ratio = {ratio}", (0, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.imshow("result", frame)
        cv2.setMouseCallback("result", onMouse)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('e'):
            lang = "eng"
        elif k == ord('j'):
            lang = "jpn"
    cap.release()
    cv2.destroyAllWindows()
    shutil.rmtree('img')


if __name__ == "__main__":
    ratio = 1
    main()
