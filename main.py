import cv2
import pyocr
import sys, os
from PIL import Image
import shutil
import subprocess


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


def main():
    cap = cv2.VideoCapture(0)
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        sys.exit(1)
    tool = tools[0]

    if os.path.isdir("img"):
        shutil.rmtree("img")
    os.mkdir("img")

    while cap.isOpened():
        r, frame = cap.read()
        if not r:
            break
        # OpenCVでの加工
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_TOZERO + cv2.THRESH_OTSU)

        # OCR
        img_pil = cv2pil(thresh)
        res = tool.image_to_string(img_pil,
                                   lang="eng",
                                   builder=pyocr.builders.LineBoxBuilder())
        for d in res:
            keyword = d.content.replace(" ", "_")
            if os.path.isfile(f"img/{keyword}.png"):  # すでに画像があったら貼り付け
                try:
                    tmp = cv2.imread(f"img/{keyword}.png")
                    frame[d.position[0][1]:d.position[0][1]+tmp.shape[0], d.position[1][0]:d.position[1][0]+tmp.shape[1]] = tmp
                except Exception as e:
                    print(keyword, e)
            else:  # なかったら検索してくる
                subprocess.Popen(f"python scraper.py {d.content}",
                                 cwd="D:/Users/tocky/Documents/exp_3A/OpenCV_GL/last", shell=True)
            # cv2.rectangle(frame, d.position[0], d.position[1], (0, 0, 255), 2)

        cv2.imshow("", frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    shutil.rmtree('img')


if __name__ == "__main__":
    main()