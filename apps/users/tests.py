from django.test import TestCase
from apps.users.models import MyUser
from django.contrib import auth


class UserAuthentification(TestCase):
    """Test the user registration and log in."""

    def setUp(self):
        """Create and populate a testing database."""
        self.credentials = {"email": "test@email.com", "password": "testing1234"}
        self.new_user = MyUser.objects.create_user(**self.credentials)

    def test_register(self):
        """Check if registering a new user works."""
        self.assertEqual(self.credentials["email"], self.new_user.email)

    def test_login(self):
        """Check if user login works."""
        self.new_user = auth.get_user(self.client)
        self.assertFalse(self.new_user.is_authenticated)
        self.new_user = auth.authenticate(**self.credentials)
        self.assertTrue(self.new_user.is_authenticated)
