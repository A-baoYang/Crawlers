import pytest
import time
import json
import random
import multiprocessing
from fake_useragent import UserAgent
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import seleniumwire.undetected_chromedriver as uc


class TestVideoView:
    def __init__(self):
        # self.ua = UserAgent(browsers=["chrome"])
        self.target_url = "https://www.youtube.com/watch?v=Timpnus81h0"
        self.proxy_username = "user-abaoyang-sessionduration-1"
        self.proxy_password = "abaotest"
        self.proxy_hostname = "tw.smartproxy.com"

        self.driver = uc.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.options = Options()
        # disable cookie
        self.options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.cookies": 2}
        )
        # set proxy
        # self.proxy = Proxy()
        # self.proxy.proxy_type = ProxyType.MANUAL
        # self.capabilities = DesiredCapabilities.CHROME

    def teardown_method(self):
        self.driver.quit()

    def change_proxy_and_useragent(self):
        self.random_port = random.randint(20000, 20100)
        pick_proxy = f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_hostname}:{self.random_port}"
        print(pick_proxy)

        # self.proxy.http_proxy = pick_proxy
        # self.proxy.socks_version = 5
        # self.proxy.socks_proxy = pick_proxy
        # self.proxy.ssl_proxy = pick_proxy
        # self.proxy.add_to_capabilities(self.capabilities)

        # set proxy in seleniumwire_options
        self.seleniumwire_options = {
            "proxy": {
                "http": pick_proxy,
                "verify_ssl": False,
            },
        }

        # print(self.ua.random)
        # self.options.add_argument(f"user-agent={self.ua.random}")
        self.driver = uc.Chrome(
            # desired_capabilities=self.capabilities,
            seleniumwire_options=self.seleniumwire_options,
            chrome_options=self.options,
        )

    def check_proxy_vaild(self):
        self.driver.get("http://api.ipify.org/?format=json")
        return self.driver.find_element("xpath", "//pre").text

    def execute(self):
        self.driver.get(self.target_url)
        actions = ActionChains(self.driver)
        time.sleep(5)

        while self.driver.current_url.startswith(self.target_url):

            play_btn = self.driver.find_element(
                By.XPATH, '//button[contains(@class, "ytp-play-button")]'
            ).get_attribute("title")
            if play_btn.startswith("播放"):
                actions.send_keys(Keys.SPACE).perform()

            time.sleep(random.randint(5, 15))
            self.driver.find_element("xpath", "//body").send_keys(Keys.END)
            time.sleep(random.randint(1, 3))
            self.driver.find_element("xpath", "//body").send_keys(Keys.END)
            print("Scroll down")
            time.sleep(random.randint(1, 3))
            self.driver.find_element("xpath", "//body").send_keys(Keys.HOME)
            print("Scroll up")

        print("Finish video play")
        return "Success"


def video_view(i):
    test = TestVideoView()
    test.change_proxy_and_useragent()
    # current_ip = test.check_proxy_vaild()
    # print(f"Current IP: {current_ip}")
    task_status = test.execute()
    print(f"Task status: {task_status}")
    test.teardown_method()
    return "Success"


def mp_videoview(num_process=5, num_tasks=100):
    with multiprocessing.Pool(num_process) as p:
        res = p.map(video_view, list(range(num_tasks)))
    return res


if __name__ == "__main__":
    # cumutime = 0
    # while cumutime < 12 * 60 * 60:
    #     start = time.time()
    #     try:
    #         data = mp_videoview(num_process=15)
    #         print(data)
    #     except:
    #         pass
    #     time_spent = time.time() - start
    #     print("Time taken: ", time_spent)
    #     cumutime += time_spent
    #     print("Cumulated Time taken: ", cumutime)

    data = mp_videoview(num_process=5, num_tasks=100)
    print(data)
