from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.keys import Keys
from seleniumrequests import Chrome
from serial import myserial

class WebControl():
    def __init__(self):
        self.options = webdriver.ChromeOptions()

        # ctrl + F4
        self.options.add_argument('--kiosk')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver',  chrome_options=self.options)
        self.driver.get('http://0.0.0.0:5000/home')
    
    def home(self):
        self.driver.get('http://0.0.0.0:5000/home')

    def run(self, url, args=None):
        self.driver.get(url)
        

    def exit(self):
        self.driver.quit()
        