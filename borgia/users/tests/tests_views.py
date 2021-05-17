from django.http import response
from django.test import Client
from django.test.testcases import TestCase
from django.urls import reverse

from borgia.tests.utils import get_login_url_redirected
from borgia.tests.tests_views import BaseBorgiaViewsTestCase
from borgia.utils import get_members_group
from users.models import User


class UserListViewTestCase(BaseBorgiaViewsTestCase, TestCase):
    url_view = 'url_user_list'

    def test_other_test(self):
        # Group permission tests are in BaseBorgiaViewsTestCase !

        # Others tests here if needed.
        pass
