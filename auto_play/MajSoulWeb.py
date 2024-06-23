from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import numpy as np
from io import BytesIO
import cv2
import threading
import time


class MajSoulWeb:
    def __init__(
        self,
        proxy_port:str|int|None="23410",
        chrome_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    ):
        self.proxy_server = "127.0.0.1:"+str(proxy_port) if None else None
        self.chrome_path = chrome_path
        self.driver = self._setup_driver()
        threading.Thread(target=self.main).start()

    def _setup_driver(self):
        options = webdriver.ChromeOptions()
        if self.proxy_server:
            options.add_argument(f"--proxy-server={self.proxy_server}")
            options.add_argument("--ignore-certificate-errors")
        options.binary_location = self.chrome_path

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        return driver

    def open_game_page(self, url="https://game.maj-soul.com/1/"):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "layaCanvas"))
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
        
    def main(self):
        time.sleep(10)
        self.open_game_page()