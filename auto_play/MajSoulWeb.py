from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import numpy as np
from io import BytesIO
import cv2
import threading
import time
import traceback
import os
from auto_play.RequestsProxy import RequestsProxy
from auto_play.MahjongHelper import MahjongHelper
import json
import atexit
from collections import Counter
import random


class MajSoulWeb:
    def __init__(
        self, proxy_port: str | int | None = "23410", helper: MahjongHelper = None
    ):
        self.helper = helper
        self.proxy_server = "127.0.0.1:" + str(proxy_port) if proxy_port else None
        self.proxy = RequestsProxy("http://" + self.proxy_server)
        # self.chrome_path = chrome_path
        self.driver = self._setup_driver()
        self.open_wait_page()
        self.action = ActionChains(self.driver)
        self.lock = threading.Lock()
        self.status = []
        self.maj = []
        threading.Thread(target=self.get_status).start()
        threading.Thread(target=self.main).start()

    def _setup_driver(self):
        options = webdriver.ChromeOptions()
        if self.proxy_server:
            options.add_argument(f"--proxy-server={self.proxy_server}")
        # options.add_argument("--ignore-certificate-errors")
        print("Chrome Options: ", options.arguments)

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        return driver

    def open_wait_page(self, url="auto_play/wait.html"):
        self.driver.get(os.path.abspath(url))

    def open_game_page(self, url="https://game.maj-soul.com/1/"):
        self.driver.get(url)

    def save_data(self):
        # 保存Cookies
        with open("config/cookies.json", "w") as f:
            json.dump(self.driver.get_cookies(), f, indent=4)

        # 保存localStorage数据
        local_storage = self.driver.execute_script(
            "return JSON.stringify(localStorage);"
        )
        local_storage_data = json.loads(local_storage)
        with open("config/local_storage.json", "w") as local_file:
            json.dump(local_storage_data, local_file, indent=4)

    def read_data(self):
        # 读取并添加Cookies
        if os.path.exists("config/cookies.json"):
            with open("config/cookies.json", "r") as f:
                cookies = json.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            self.driver.refresh()

        # 读取并设置localStorage数据
        if os.path.exists("config/local_storage.json"):
            with open("config/local_storage.json", "r") as local_file:
                local_storage_data = json.load(local_file)
                for key, value in local_storage_data.items():
                    self.driver.execute_script(
                        f"localStorage.setItem('{key}', '{value}');"
                    )

    def get_image(self):
        screenshot = self.driver.get_screenshot_as_png()
        image = Image.open(BytesIO(screenshot))
        image_array = np.array(image)
        return image_array[:, :, ::-1]

    def get_size(self, image: np.array) -> tuple:
        return tuple(reversed(image.shape[:2]))

    def get_padding(self, size: tuple) -> tuple:
        width, height = size
        target_ratio = 16 / 9

        if width / height > target_ratio:
            rect_height = height
            rect_width = int(height * target_ratio)
        else:
            rect_width = width
            rect_height = int(width / target_ratio)

        x_padding = (width - rect_width) // 2
        y_padding = (height - rect_height) // 2

        return (rect_width, rect_height), (x_padding, y_padding)

    def cut_image(self, image: np.ndarray, padding: tuple) -> np.ndarray:
        x_padding, y_padding = padding
        height, width = image.shape[:2]

        x_start = x_padding
        x_end = width - x_padding
        y_start = y_padding
        y_end = height - y_padding

        cut_img = image[y_start:y_end, x_start:x_end]

        return cut_img

    def process_and_display(self):
        image = self.get_image()
        size = self.get_size(image)
        rect, padding = self.get_padding(size)
        image = self.cut_image(image, padding)
        cv2.imshow("maj-soul", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_status(self):
        while True:
            while output := self.helper.get_output():
                with self.lock:
                    # print(output.encode())
                    self.status.append(output)
            time.sleep(0.1)

    def transfer(self, data: str) -> list[str]:
        tile_dict = {
            "m": "万",
            "p": "饼",
            "s": "索",
            "z": ["", "东", "南", "西", "北", "白", "发", "中"],
        }

        tiles = []
        parts = data.split()

        for part in parts:
            length = len(part)
            for i in range(length - 1):
                if part[i].isdigit():
                    num = int(part[i])
                    tile_type = part[length - 1]
                    if tile_type in tile_dict:
                        if tile_type == "z":
                            tiles.append(tile_dict[tile_type][num])
                        elif num == 0:
                            tiles.append(f"红5{tile_dict[tile_type]}")
                        else:
                            tiles.extend([f"{num}{tile_dict[tile_type]}"])

        return tiles

    def find_extra_element(self, list1, list2):
        counter1 = Counter(list1)
        counter2 = Counter(list2)

        for element in counter1:
            if counter1[element] > counter2[element]:
                return [element]

        return []

    def click(self, p_x, p_y):
        image = self.get_image()
        size = self.get_size(image)
        rect, padding = self.get_padding(size)
        ratio = self.driver.execute_script("return window.innerWidth;") / size[0]
        x = int((rect[0] * p_x - rect[0] // 2) * ratio)
        y = int((rect[1] * p_y - rect[1] // 2) * ratio)

        element = self.driver.find_element(By.TAG_NAME, "canvas")
        self.action.move_to_element_with_offset(element, x, y).click().pause(
            0.1
        ).click().perform()

    def put_maj(self, maj):
        index = self.maj.index(maj)
        print(index)
        index_ = self.maj_.index(maj)
        self.maj_.pop(index_)
        self.maj = self.maj_
        ori_x = 389 / 2796
        ori_y = 1456 / 1572
        x_pass = 1783 / 2796 / 13
        time.sleep(random.uniform(2, 5))
        self.click(ori_x + x_pass * index, ori_y)

    def skip_maj(self):
        time.sleep(random.uniform(1, 3))
        self.click(1900 / 2796, 1210 / 1572)

    def get_strategy(self):
        flag = -1
        with self.lock:
            for index, value in enumerate(self.status):
                if value.find("=====") != -1:
                    flag = index
                    break
        if flag == -1:
            return None
        index = flag
        time.sleep(0.5)
        with self.lock:
            for i in range(index):
                if self.status[i].find("即将开始") != -1:
                    self.maj = []
                if self.status[i].find("和牌") != -1:
                    self.maj = []
                if self.status[i].find("本局结束") != -1:
                    self.maj = []
                if self.status[i].find("流局") != -1:
                    self.maj = []
            if self.status[index - 1].find("+") != -1:
                self.status = self.status[index + 1 :]
                return "skip"
            maj = self.transfer(self.status[index - 1])
            self.maj_ = list(maj)
            if not self.maj:
                self.maj = maj
            else:
                self.maj += self.find_extra_element(maj, self.maj)
            if len(self.maj) == 13:
                self.status = self.status[index + 1 :]
                return None
            if len(self.maj) > 14:
                self.maj = []
                return
            index += 1
            if self.status[index].find("倒退") != -1:
                index += 1
            index += 1
            print(self.maj)
            for i in self.maj:
                if self.status[index].find(i) != -1:
                    self.status = self.status[index:]
                    return i

    def main(self):
        while True:
            try:
                self.proxy.get("http://www.baidu.com")
                self.open_game_page()
                self.read_data()
                atexit.register(self.save_data)
                break
            except:
                pass

        while True:
            try:
                if strategy := self.get_strategy():
                    if strategy == "skip":
                        print("跳过")
                        self.skip_maj()
                    else:
                        print(f"出牌：{strategy}")
                        self.put_maj(strategy)
            except:
                print(traceback.format_exc())
                break

        while True:
            try:
                exec(input())
            except:
                print(traceback.format_exc())
