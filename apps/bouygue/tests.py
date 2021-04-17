from apps.users.models import MyUser
from apps.activities.models import Activity
from apps.agenda.models import Reservation
from apps.blog.models import Post, Comment
from apps.info.models import InfoPost
from apps.work.models import Work

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
        executable_path="C:/Users/Guillaume/Desktop/Formation OPC/P13_merle_guillaume/config/chromedriver.exe"
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
        pass
        # Category.objects.create(name="boisson")
        # self.pepsi = Product.objects.create(id=1, name="pepsi", nutriscore="E")
        # self.fanta = Product.objects.create(id=2, name="fanta", nutriscore="C")
        # self.apple_juice = Product.objects.create(
        #     id=3, name="jus de pomme", nutriscore="B"
        # )

        # self.products = Product.objects.all()
        # self.category = Category.objects.first()

        # for product in self.products:
        #     product.categories.add(self.category)

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
        # fill registration form
        self.selenium.get("%s%s" % (self.live_server_url, "/register/"))
        name_input = self.selenium.find_element_by_name("name")
        name_input.send_keys("John")
        surname_input = self.selenium.find_element_by_name("surname")
        surname_input.send_keys("Doe")
        username_input = self.selenium.find_element_by_name("email")
        username_input.send_keys("test@email.com")
        password_input = self.selenium.find_element_by_name("password1")
        password_input.send_keys("testing1234")
        password_input = self.selenium.find_element_by_name("password2")
        password_input.send_keys("testing1234")
        self.selenium.find_element_by_name("register").click()
        self.assertEqual(
            "test@email.com", MyUser.objects.get(email="test@email.com").email
        )

    def test_login(self):
        # register
        self.test_register()
        user = MyUser.objects.first()
        user.is_active = True
        user.save()
        # fill login form
        self.selenium.get("%s%s" % (self.live_server_url, "/login/"))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys("test@email.com")
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys("testing1234")
        self.selenium.find_element_by_name("login").click()
        self.assertTrue(MyUser.objects.get(email="test@email.com").is_authenticated)

    def test_logout(self):
        # register and login
        self.test_register()
        self.test_login()
        # click logout button
        self.selenium.get("%s%s" % (self.live_server_url, "/"))
        try:
            self.selenium.find_element_by_id("navbar-button").click()
            self.selenium.find_element_by_id("logout-icon").click()
        except exceptions.ElementNotInteractableException:
            self.selenium.find_element_by_id("logout-icon").click()
        self.selenium.get("%s%s" % (self.live_server_url, "/profile"))
        url = driver.current_url
        self.assertEqual(url, self.live_server_url + "/login/?next=/profile/")

    def test_add_post(self):
        # register and login
        self.test_register()
        self.test_login()
        # create blog post
        self.selenium.find_element_by_name("blog").click()
        self.selenium.find_element_by_name("new").click()
        username_input = self.selenium.find_element_by_name("title")
        username_input.send_keys("my title")
        password_input = self.selenium.find_element_by_name("content")
        password_input.send_keys("my content")
        self.selenium.find_element_by_name("create").click()
        # check if post is created
        post = Post.objects.first()
        post_title = post.title
        self.assertEqual("my title", post_title)

    def test_update_post(self):
        # register, login and create blog post
        self.test_add_post()
        # update post
        self.selenium.find_element_by_name("update-post").click()
        title_input = self.selenium.find_element_by_name("title")
        title_input.send_keys(" is updated")
        content_input = self.selenium.find_element_by_name("content")
        content_input.send_keys(" is updated")
        self.selenium.find_element_by_name("update").click()
        # check if post is updated
        post = Post.objects.first()
        post_new_title = post.title
        self.assertEqual("my title is updated", post_new_title)

    def test_delete_post(self):
        # register, login and create blog post
        self.test_add_post()
        # delete post
        self.selenium.find_element_by_name("delete-post").click()
        self.selenium.find_element_by_name("delete").click()
        # check if post is deleted
        post = Post.objects.all()
        self.assertEqual(0, len(post))

    def test_add_comment(self):
        # register, login and create blog post
        self.test_add_post()
        # create comment
        comment_input = self.selenium.find_element_by_name("content")
        comment_input.send_keys("my comment")
        self.selenium.find_element_by_name("send").click()
        # check if comment is created
        post = Post.objects.first()
        comment = post.comment_set.first()
        comment_content = comment.content
        self.assertEqual("my comment", comment_content)

    def test_update_comment(self):
        # register, login and create blog comment
        self.test_add_comment()
        # update comment
        self.selenium.find_element_by_name("update-comment").click()
        content_input = self.selenium.find_element_by_name("content")
        content_input.send_keys(" is updated")
        self.selenium.find_element_by_name("update").click()
        # check if comment is updated
        post = Post.objects.first()
        comment = post.comment_set.first()
        comment_new_content = comment.content
        self.assertEqual("my comment is updated", comment_new_content)

    def test_delete_comment(self):
        # register, login and create blog comment
        self.test_add_comment()
        # delete comment
        self.selenium.find_element_by_name("delete-comment").click()
        self.selenium.find_element_by_name("delete").click()
        # check if comment is deleted
        post = Post.objects.first()
        comment = post.comment_set.all()
        self.assertEqual(0, len(comment))
