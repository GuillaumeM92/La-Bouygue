import os
from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from apps.users.models import MyUser
from apps.activities.models import Activity
from apps.agenda.models import Reservation
from apps.blog.models import Post
from apps.info.models import InfoPost
from apps.work.models import Work
from apps.budget.models import Budget, Funding


# -------------------------- SELENIUM TESTS ---------------------------
if os.name == "nt":
    driver = webdriver.Chrome(
        executable_path=("C:/Users/Guillaume/Desktop/Formation OPC/P13_merle_guillaume"
                         "/config/chromedriver.exe")
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
        name_input.send_keys("Doe")
        surname_input = self.selenium.find_element_by_name("surname")
        surname_input.send_keys("John")
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

    # BLOG
    def test_add_post(self):
        # register and login
        self.test_register()
        self.test_login()
        # create blog post
        self.selenium.find_element_by_name("blog").click()
        self.selenium.find_element_by_name("new").click()
        title_input = self.selenium.find_element_by_name("title")
        title_input.send_keys("my title")
        content_input = self.selenium.find_element_by_name("content")
        content_input.send_keys("my content")
        self.selenium.find_element_by_name("create").click()
        # check if post is created
        post = Post.objects.first()
        self.assertEqual("my title", post.title)

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
        self.assertEqual("my title is updated", post.title)

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
        self.assertEqual("my comment", comment.content)

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
        self.assertEqual("my comment is updated", comment.content)

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

    # INFO
    def test_add_infopost(self):
        # register and login
        self.test_register()
        self.test_login()
        # make user admin
        user = MyUser.objects.first()
        user.is_staff = True
        user.save()
        # create infopost
        self.selenium.find_element_by_name("info").click()
        self.selenium.find_element_by_name("new").click()
        title_input = self.selenium.find_element_by_name("title")
        title_input.send_keys("my title")
        content_input = self.selenium.find_element_by_name("content")
        content_input.send_keys("my content")
        self.selenium.find_element_by_name("create").click()
        # check if infopost is created
        infopost = InfoPost.objects.first()
        self.assertEqual("my title", infopost.title)

    def test_update_infopost(self):
        # register, login and create blog infopost
        self.test_add_infopost()
        # update infopost
        self.selenium.find_element_by_name("update-infopost").click()
        title_input = self.selenium.find_element_by_name("title")
        title_input.send_keys(" is updated")
        content_input = self.selenium.find_element_by_name("content")
        content_input.send_keys(" is updated")
        self.selenium.find_element_by_name("update").click()
        # check if infopost is updated
        infopost = InfoPost.objects.first()
        self.assertEqual("my title is updated", infopost.title)

    def test_delete_infopost(self):
        # register, login and create blog infopost
        self.test_add_infopost()
        # delete infopost
        self.selenium.find_element_by_name("delete-infopost").click()
        self.selenium.find_element_by_name("delete").click()
        # check if infopost is deleted
        infopost = InfoPost.objects.all()
        self.assertEqual(0, len(infopost))

    def test_add_infocomment(self):
        # register, login and create blog infopost
        self.test_add_infopost()
        # create infocomment
        infocomment_input = self.selenium.find_element_by_name("content")
        infocomment_input.send_keys("my infocomment")
        self.selenium.find_element_by_name("send").click()
        # check if infocomment is created
        infopost = InfoPost.objects.first()
        infocomment = infopost.infocomment_set.first()
        self.assertEqual("my infocomment", infocomment.content)

    def test_update_infocomment(self):
        # register, login and create blog infocomment
        self.test_add_infocomment()
        # update infocomment
        self.selenium.find_element_by_name("infocomment-update").click()
        content_input = self.selenium.find_element_by_name("content")
        content_input.send_keys(" is updated")
        self.selenium.find_element_by_name("update").click()
        # check if infocomment is updated
        infopost = InfoPost.objects.first()
        infocomment = infopost.infocomment_set.first()
        self.assertEqual("my infocomment is updated", infocomment.content)

    def test_delete_infocomment(self):
        # register, login and create blog infocomment
        self.test_add_infocomment()
        # delete infocomment
        self.selenium.find_element_by_name("infocomment-delete").click()
        self.selenium.find_element_by_name("delete").click()
        # check if infocomment is deleted
        infopost = InfoPost.objects.first()
        infocomment = infopost.infocomment_set.all()
        self.assertEqual(0, len(infocomment))

    # ACTIVITIES
    def test_add_activity(self):
        # register and login
        self.test_register()
        self.test_login()
        # create activity
        self.selenium.find_element_by_name("activities").click()
        self.selenium.find_element_by_name("new").click()
        title_input = self.selenium.find_element_by_name("title")
        title_input.send_keys("my title")
        content_input = self.selenium.find_element_by_name("content")
        content_input.send_keys("my content")
        content2_input = self.selenium.find_element_by_name("content2")
        content2_input.send_keys("my content2")
        duration_input = self.selenium.find_element_by_name("duration")
        duration_input.send_keys("1h")
        distance_input = self.selenium.find_element_by_name("distance")
        distance_input.send_keys("15mn")
        self.selenium.find_element_by_name("create").click()
        # check if activity is created
        activity = Activity.objects.first()
        self.assertEqual("my title", activity.title)

    def test_update_activity(self):
        # register, login and create activity
        self.test_add_activity()
        # update activity
        self.selenium.find_element_by_name("update-activity").click()
        title_input = self.selenium.find_element_by_name("title")
        title_input.send_keys(" is updated")
        content_input = self.selenium.find_element_by_name("content")
        content_input.send_keys(" is updated")
        self.selenium.find_element_by_name("update").click()
        # check if activity is updated
        activity = Activity.objects.first()
        self.assertEqual("my title is updated", activity.title)

    def test_delete_activity(self):
        # register, login and create activity
        self.test_add_activity()
        # delete activity
        self.selenium.find_element_by_name("delete-activity").click()
        self.selenium.find_element_by_name("delete").click()
        # check if activity is deleted
        activity = Activity.objects.all()
        self.assertEqual(0, len(activity))

    def test_add_activitycomment(self):
        # register, login and create activity
        self.test_add_activity()
        # create comment
        comment_input = self.selenium.find_element_by_name("content")
        comment_input.send_keys("my comment")
        self.selenium.find_element_by_name("send").click()
        # check if comment is created
        activity = Activity.objects.first()
        comment = activity.activitycomment_set.first()
        self.assertEqual("my comment", comment.content)

    def test_update_activitycomment(self):
        # register, login and create activity comment
        self.test_add_activitycomment()
        # update comment
        self.selenium.find_element_by_name("activitycomment-update").click()
        content_input = self.selenium.find_element_by_name("content")
        content_input.send_keys(" is updated")
        self.selenium.find_element_by_name("update").click()
        # check if comment is updated
        activity = Activity.objects.first()
        comment = activity.activitycomment_set.first()
        self.assertEqual("my comment is updated", comment.content)

    def test_delete_activitycomment(self):
        # register, login and create activity comment
        self.test_add_activitycomment()
        # delete comment
        self.selenium.find_element_by_name("activitycomment-delete").click()
        self.selenium.find_element_by_name("delete").click()
        # check if comment is deleted
        activity = Activity.objects.first()
        comment = activity.activitycomment_set.all()
        self.assertEqual(0, len(comment))

    # WORK
    def test_add_work(self):
        # register and login
        self.test_register()
        self.test_login()
        # create work
        self.selenium.find_element_by_name("work").click()
        self.selenium.find_element_by_name("new").click()
        title_input = self.selenium.find_element_by_name("title")
        title_input.send_keys("my title")
        content_input = self.selenium.find_element_by_name("content")
        content_input.send_keys("my content")
        cost_input = self.selenium.find_element_by_name("cost")
        cost_input.send_keys("15")
        self.selenium.find_element_by_name("create").click()
        # check if work is created
        work = Work.objects.first()
        self.assertEqual("my title", work.title)

    def test_update_work(self):
        # register, login and create work
        self.test_add_work()
        # update work
        self.selenium.find_element_by_name("update-work").click()
        title_input = self.selenium.find_element_by_name("title")
        title_input.send_keys(" is updated")
        content_input = self.selenium.find_element_by_name("content")
        content_input.send_keys(" is updated")
        self.selenium.find_element_by_name("update").click()
        # check if work is updated
        work = Work.objects.first()
        self.assertEqual("my title is updated", work.title)

    def test_delete_work(self):
        # register, login and create work
        self.test_add_work()
        # delete work
        self.selenium.find_element_by_name("delete-work").click()
        self.selenium.find_element_by_name("delete").click()
        # check if work is deleted
        work = Work.objects.all()
        self.assertEqual(0, len(work))

    def test_add_workcomment(self):
        # register, login and create work
        self.test_add_work()
        # create comment
        comment_input = self.selenium.find_element_by_name("content")
        comment_input.send_keys("my comment")
        self.selenium.find_element_by_xpath(
            '//*[@id="layoutDefault"]/div[2]/section/div[1]/div/div[3]/'
            'div/form/fieldset/button').click()
        # check if comment is created
        work = Work.objects.first()
        comment = work.workcomment_set.first()
        self.assertEqual("my comment", comment.content)

    def test_update_workcomment(self):
        # register, login and create work comment
        self.test_add_workcomment()
        # update comment
        self.selenium.find_element_by_name("workcomment-update").click()
        content_input = self.selenium.find_element_by_name("content")
        content_input.send_keys(" is updated")
        self.selenium.find_element_by_name("update").click()
        # check if comment is updated
        work = Work.objects.first()
        comment = work.workcomment_set.first()
        self.assertEqual("my comment is updated", comment.content)

    def test_delete_workcomment(self):
        # register, login and create work comment
        self.test_add_workcomment()
        # delete comment
        self.selenium.find_element_by_name("workcomment-delete").click()
        self.selenium.find_element_by_name("delete").click()
        # check if comment is deleted
        work = Work.objects.first()
        comment = work.workcomment_set.all()
        self.assertEqual(0, len(comment))

    def test_work_done(self):
        # register, login and create work
        self.test_add_work()
        # click work completed button
        self.selenium.find_element_by_name("action").click()
        # check if work status has changed
        work = Work.objects.first()
        # here 2 is equivalent to a completed work, value was set to 0 on creation
        self.assertEqual("Terminé", work.get_state_display())

    def test_comment_posted_on_work_done(self):
        # register, login and create work
        self.test_add_work()
        # click work completed button
        self.selenium.find_element_by_name("action").click()
        # check if work done comment was posted
        work = Work.objects.first()
        comment = work.workcomment_set.first()
        self.assertEqual(
            "John Doe vient de signaler qu'il a terminé ce travail.", comment.content)

    # BUDGET
    def test_add_budget(self):
        # register and login
        self.test_register()
        self.test_login()
        # make user admin
        user = MyUser.objects.first()
        user.is_staff = True
        user.save()
        # create budget
        self.selenium.find_element_by_name("budget").click()
        self.selenium.find_element_by_name("create-budget").click()
        total_input = self.selenium.find_element_by_name("total")
        total_input.send_keys("42")
        description_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="id_description"]')))
        description_input.send_keys("my description")
        self.selenium.find_element_by_name("update").click()
        # check if budget is created
        budget = Budget.objects.first()
        # 420 because there is a trailing zero already in the field
        self.assertEqual(420, budget.total)

    def test_add_funding(self):
        # register and login
        self.test_register()
        self.test_login()
        # make user admin
        user = MyUser.objects.first()
        user.is_staff = True
        user.save()
        # create funding
        self.selenium.find_element_by_name("budget").click()
        self.selenium.find_element_by_name("funding-menu").click()
        self.selenium.find_element_by_name("add-funding").click()
        progress_input = self.selenium.find_element_by_name("progress")
        progress_input.send_keys("24")
        goal_input = self.selenium.find_element_by_name("goal")
        goal_input.send_keys("42")
        self.selenium.find_element_by_name("update").click()
        # check if funding is created
        funding = Funding.objects.first()
        # 240 because there is a trailing zero already in the field
        self.assertEqual(240, funding.progress)

    # AGENDA
    def test_add_reservation(self):
        # register and login
        self.test_register()
        self.test_login()
        # create reservation
        self.selenium.find_element_by_name("calendar").click()
        self.selenium.find_element_by_name("new").click()
        name_input = self.selenium.find_element_by_name("name")
        name_input.send_keys("my name")
        start_date_input = self.selenium.find_element_by_name("start_date")
        start_date_input.send_keys("18/04/2021")
        end_date_input = self.selenium.find_element_by_name("end_date")
        end_date_input.send_keys("23/04/2021")
        description_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="id_description"]')))
        description_input.send_keys("my description")
        self.selenium.find_element_by_name("create").click()
        # check if reservation is created
        reservation = Reservation.objects.first()
        self.assertEqual("my name", reservation.name)
