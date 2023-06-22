import pytest
import time
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class TestVideoView:
    def __init__(self):
        self.proxy_pool = [f"http://user-abaoyang-sessionduration-1:abaotest@tw.smartproxy.com:{i}" for i in range(20000, 20100)]
        self.options = Options()
        self.vars = {}

    def teardown_method(self):
        self.driver.quit()

    def change_proxy(self):
        pick_proxy = random.choice(self.proxy_pool)
        self.options.add_argument(f"--proxy-server={pick_proxy}")
        self.driver = webdriver.Chrome(options=self.options)

    def execute(self):
        self.driver.get("https://youtu.be/Timpnus81h0")
        for i in range(10):
            self.driver.execute_script("window.scrollTo(0, Y)")
            sleep(random.randint(5, 30))
            self.driver.execute_script("window.scrollTo(0, 0)")
            sleep(random.randint(5, 30))
