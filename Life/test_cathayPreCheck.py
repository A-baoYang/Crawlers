# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class TestCathayPreCheck:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self):
        self.driver.quit()

    def test_cathayPreCheck(self):
        # Test name: Cathay Checkin
        # Step # | name | target | value
        # 1 | open | https://go.linyuan.com.tw/FKWeb/servlet/HttpDispatcher/FKZ5_3000/prompt?eBAF_loginPlatformInfo=HZK6V7kAY3aUZCQzBT%2F1u%2FQ0vgGOgPpRTIoI3ruBJfPsnxHdsvHR4RFBjWui5dxXTAoxrNcD8C5AmCG8wdNL8sSQdTQ2%2BNnCH8w%2Fihb4tXs%3D&&_=1679850977064 |
        self.driver.get(
            "https://go.linyuan.com.tw/FKWeb/servlet/HttpDispatcher/FKZ5_3000/prompt?eBAF_loginPlatformInfo=HZK6V7kAY3aUZCQzBT%2F1u%2FQ0vgGOgPpRTIoI3ruBJfPsnxHdsvHR4RFBjWui5dxXTAoxrNcD8C5AmCG8wdNL8sSQdTQ2%2BNnCH8w%2Fihb4tXs%3D&&_=1679850977064"
        )
        # 2 | setWindowSize | 1382x816 |
        self.driver.set_window_size(1382, 816)
        # 3 | click | id=UID |
        self.driver.find_element(By.ID, "UID").click()
        # 4 | type | id=UID | 00509436
        self.driver.find_element(By.ID, "UID").send_keys("00509436")
        # 5 | click | id=KEY |
        self.driver.find_element(By.ID, "KEY").click()
        # 6 | type | id=KEY | C@thay12YGyang61501
        self.driver.find_element(By.ID, "KEY").send_keys("C@thay12YGyang61501")
        # 7 | click | id=btnLogin |
        self.driver.find_element(By.ID, "btnLogin").click()
        # 8 | waitForElementPresent | css=#checkInBtn > .clip_text:nth-child(1) | 30000
        WebDriverWait(self.driver, 300).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, "#checkInBtn > .clip_text:nth-child(1)")
            )
        )
        print("PreCheck Success")


if __name__ == "__main__":
    test = TestCathayPreCheck()
    test.setup_method()
    test.test_cathayPreCheck()
    test.teardown_method()