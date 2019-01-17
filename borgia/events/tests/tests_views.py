import datetime
import decimal

from django.test import Client
from django.urls import reverse

from borgia.tests.tests_views import BaseBorgiaViewsTestCase
from borgia.tests.utils import get_login_url_redirected
from events.models import Event


class BaseEventsViewsTestCase(BaseBorgiaViewsTestCase):
    """
    Base for Events views tests.
    Users : user1 (all permissions), user2 (no permissions), user3 (manager of event1).
    Event :
     - event1, managed by user3.
     - event2, managed by user3, done
    """
    def setUp(self):
        super().setUp()

        self.event1 = Event.objects.create(
            description='The first event',
            date=datetime.date(2053, 1, 1),
            manager=self.user3,
            price=decimal.Decimal(1000.00)
        )
        self.event2 = Event.objects.create(
            description='The second event',
            date=datetime.date(2053, 1, 1),
            manager=self.user3,
            price=decimal.Decimal(1000.00),
            done=True
        )


class BaseGeneralEventViewsTestCase(BaseEventsViewsTestCase):
    url_view = None

    def get_url(self):
        return reverse(self.url_view)

    def allowed_user_get(self):
        response_client1 = self.client1.get(self.get_url())
        self.assertEqual(response_client1.status_code, 200)

    def not_allowed_user_get(self):
        response_client2 = self.client2.get(self.get_url())
        response_client3 = self.client3.get(self.get_url())
        self.assertEqual(response_client2.status_code, 403)
        self.assertEqual(response_client3.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url())
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(self.get_url()))


class EventListViewTests(BaseGeneralEventViewsTestCase):
    url_view = 'url_event_list'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class EventCreateViewTests(BaseGeneralEventViewsTestCase):
    url_view = 'url_event_create'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class BaseFocusEventViewsTestCase(BaseEventsViewsTestCase):
    """
    Implement tests for views when focusing on an event.
    """
    url_view = None

    def get_url(self, event_pk):
        return reverse(self.url_view, kwargs={'pk': event_pk})

    def as_president_get(self):
        response_client1 = self.client1.get(self.get_url(self.event1.pk))
        self.assertEqual(response_client1.status_code, 200)

    def as_manager_get(self):
        response_client3 = self.client3.get(self.get_url(self.event1.pk))
        self.assertEqual(response_client3.status_code, 200)

    def not_allowed_user_get(self):
        response_client2 = self.client2.get(self.get_url(self.event1.pk))
        self.assertEqual(response_client2.status_code, 403)

    def not_existing_event_get(self):
        response_client1 = self.client1.get(self.get_url('5353'))
        self.assertEqual(response_client1.status_code, 404)

    def offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url(self.event1.pk))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(self.get_url(self.event1.pk)))


class EventUpdateViewTests(BaseFocusEventViewsTestCase):
    url_view = 'url_event_update'

    def test_as_president_get(self):
        super().as_president_get()

    def test_as_manager_get(self):
        super().as_manager_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_not_existing_event_get(self):
        super().not_existing_event_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class EventFinishViewTests(BaseFocusEventViewsTestCase):
    url_view = 'url_event_finish'

    def test_as_president_get(self):
        response_client1 = self.client1.get(self.get_url(self.event1.pk))
        self.assertEqual(response_client1.status_code, 403)

    def test_as_manager_get(self):
        response_client3 = self.client3.get(self.get_url(self.event1.pk))
        self.assertEqual(response_client3.status_code, 403)

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_not_existing_event_get(self):
        super().not_existing_event_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class EventDeleteViewTests(BaseFocusEventViewsTestCase):
    url_view = 'url_event_delete'

    def test_as_president_get(self):
        super().as_president_get()

    def test_as_manager_get(self):
        super().as_manager_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_not_existing_event_get(self):
        super().not_existing_event_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class EventManageUsersTests(BaseFocusEventViewsTestCase):
    url_view = 'url_event_manage_users'

    def test_as_president_get(self):
        super().as_president_get()

    def test_as_manager_get(self):
        super().as_manager_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_not_existing_event_get(self):
        super().not_existing_event_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()
