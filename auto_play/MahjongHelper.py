import subprocess
import threading
import queue
import os
import zipfile
import atexit
from auto_play.RequestsProxy import proxy as requests


def download_and_extract(url, extract_to="."):
    local_filename = url.split("/")[-1]
    if not os.path.exists("mahjong-helper.exe"):
        print(f"mahjong-helper.exe不存在，正在下载\n")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        with zipfile.ZipFile(local_filename, "r") as zip_ref:
            zip_ref.extractall(extract_to)

        os.remove(local_filename)
        print(f"mahjong-helper.exe下载完成\n")
    else:
        print(f"mahjong-helper.exe已存在，跳过下载\n")


url = "https://github.com/EndlessCheng/mahjong-helper/releases/download/v0.2.8/mahjong-helper-v0.2.8-win64-x64.zip"
download_and_extract(url)


class MahjongHelper:
    def __init__(self, executable_path="mahjong-helper.exe", port=12121):
        # os.system("taskkill /f /pid mahjong-helper.exe")
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.process = subprocess.Popen(
            executable_path + f" -port {port}",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",  # 使用utf-8编码
            errors="ignore",  # 忽略解码错误
            startupinfo=startupinfo,  # 隐藏窗口
        )
        self.output_queue = queue.Queue()
        self.output_thread = threading.Thread(target=self._read_output)
        self.output_thread.daemon = True
        self.output_thread.start()
        self.set_input("1")
        atexit.register(self.close)

    def _read_output(self):
        while True:
            output_line = self.process.stdout.readline()
            if output_line:
                print(output_line)
                self.output_queue.put(output_line)
            else:
                break

    def set_input(self, data):
        self.process.stdin.write(data + "\n")
        self.process.stdin.flush()

    def get_output(self):
        if not self.output_queue.empty():
            return self.output_queue.get()
        return None

    def close(self):
        self.process.terminate()
        self.process.wait()

    def __del__(self):
        self.close()


if __name__ == "__main__":
    helper = MahjongHelper("../mahjong-helper.exe")

    while True:
        if output := helper.get_output():
            print(output)
