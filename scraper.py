import requests
from bs4 import BeautifulSoup
import sys
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


def download_img(src: str):
    res = requests.get(src)
    if res.status_code == 200:
        return res.content
    else:
        return False


def search_img(keyword: str):
    try:
        url = f"https://www.google.com/search?hl=jp&q={keyword}&btnG=Google+Search&tbs=0&safe=off&tbm=isch"
        res = requests.get(url).text
        soup = BeautifulSoup(res, "html.parser")
        element = soup.select_one('img.t0fcAb')
        if not element:
            print("none: ", keyword)
            return
        img = download_img(element.get("src"))
        with open(f"img/{keyword.replace(' ', '_')}.png", "wb") as f:
            f.write(img)
    except Exception as e:
        print(keyword, e)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        search_img(" ".join(sys.argv[1:]))