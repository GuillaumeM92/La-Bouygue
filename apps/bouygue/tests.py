from .models import Product, Category
from apps.users.models import MyUser
from apps.favorites.models import Favorite
from django.test import TestCase
from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time

# -------------------------- SELENIUM TESTS ---------------------------
if os.name == "nt":
    driver = webdriver.Chrome(
        executable_path="C:/Users/Guillaume/Desktop/Formation OPC/P8_merle_guillaume"
        "/config/chromedriver.exe"
    )

else:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        "/home/travis/virtualenv/python3.8.6/chromedriver",
        chrome_options=chrome_options,
    )


class UserStorySeleniumTest(LiveServerTestCase):
    def setUp(self):
        """Create and populate a testing database."""
        Category.objects.create(name="boisson")
        self.pepsi = Product.objects.create(id=1, name="pepsi", nutriscore="E")
        self.fanta = Product.objects.create(id=2, name="fanta", nutriscore="C")
        self.apple_juice = Product.objects.create(
            id=3, name="jus de pomme", nutriscore="B"
        )

        self.products = Product.objects.all()
        self.category = Category.objects.first()

        for product in self.products:
            product.categories.add(self.category)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = driver
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_register(self):
        self.selenium.get("%s%s" % (self.live_server_url, "/register/"))
        username_input = self.selenium.find_element_by_name("email")
        username_input.send_keys("test@email.com")
        password_input = self.selenium.find_element_by_name("password1")
        password_input.send_keys("testing1234")
        password_input = self.selenium.find_element_by_name("password2")
        password_input.send_keys("testing1234")
        self.selenium.find_element_by_xpath('//button[@value="Register"]').click()
        self.assertEqual(
            "test@email.com", MyUser.objects.get(email="test@email.com").email
        )

    def test_login(self):
        self.test_register()
        self.selenium.get("%s%s" % (self.live_server_url, "/login/"))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys("test@email.com")
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys("testing1234")
        self.selenium.find_element_by_xpath('//button[@value="Log in"]').click()
        self.assertTrue(MyUser.objects.get(email="test@email.com").is_authenticated)
