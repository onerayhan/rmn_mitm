import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

class TestSelenium(unittest.TestCase):

    def setUp(self):
        # Set up Chrome options with proxy
        proxy = f"{os.getenv('PROXY_HOST', 'mitmdump')}:{os.getenv('PROXY_PORT', '8080')}"
        chrome_options = Options()
        chrome_options.add_argument(f"--proxy-server=http://{proxy}")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def test_page_load(self):
        # Open a simple test page and check title
        self.driver.get("http://example.com")
        self.assertIn("Example Domain", self.driver.title)
        print(f"Opened the page: {self.driver.title}")

        # Screenshot the page
        self.driver.save_screenshot('example_page.png')

    def test_form_fill(self):
        # Open the test form page
        self.driver.get("http://mitm.it/")
       
