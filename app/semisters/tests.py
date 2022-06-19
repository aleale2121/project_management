import json
import warnings
from http import HTTPStatus
from os.path import join

from core.models import User
# from django.contrib.auth.models import User
warnings.filterwarnings(action="ignore")

from django.conf import settings
from django.test import RequestFactory, TestCase, TransactionTestCase
from rest_framework.test import APIClient, force_authenticate

from semisters.views import SemisterViewSet


class SemisterViewSetTest(TestCase):
    test_fixtures = [
        "users",
        "semisters",
    ]

    fixtures = ["/app/fixtures/users.json", "/app/fixtures/semisters.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(username="alefew")

    def test_semister_viewset(self):
        request = self.factory.get(
            "/api/semisters",
        )
        force_authenticate(request, user=self.user)
        response = SemisterViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.data["results"][0]["name"], "One")
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)

    def test_semister_create(self):
        existing_data = json.dumps(
            {"name": "One",}
        )
        new_data = json.dumps(
            {"name": "Four"}
        )
        client = APIClient()
        client.force_authenticate(user=self.user)
        # test with existing username
        response = client.post("/api/semisters", data=existing_data, content_type="application/json")
        print(response.data)
        # self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST._value_)
        self.assertEqual(response.data["name"][0], "semister with this name already exists.")

        # test with new username
        response = client.post("/api/semisters", data=new_data, content_type="application/json")
        self.assertEqual(response.status_code, HTTPStatus.CREATED._value_)
        self.assertEqual(response.data["name"], "Four")

    def test_semister_destroy(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        # check delete using existing semisters
        response = client.delete("/api/semisters/{}".format(1))
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT._value_)

        # check delete using non existing semisters
        response = client.delete("/api/semisters/{}".format(800))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND._value_)

    def test_semister_update(self):
        data = json.dumps(
            {"name": "Three"}
        )
        client = APIClient()
        client.force_authenticate(user=self.user)
        # check update using non existing id
        response = client.put("/api/semisters/{}".format(600), data=data, content_type="application/json")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND._value_)

        # check update using existing id
        response = client.put("/api/semisters/{}".format(2), data=data, content_type="application/json")
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)
        self.assertEqual(response.data["name"], "Three")
