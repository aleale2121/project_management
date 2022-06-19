# import json
# import warnings
# from http import HTTPStatus
# from os.path import join

# from core.models import User
# # from django.contrib.auth.models import User
# from django.conf import settings
# from django.test import RequestFactory, TestCase, TransactionTestCase
# from rest_framework.test import APIClient, force_authenticate

# from users.views import StaffViewSet, StudentModelViewSet, UserViewSet,CoordinatorModelViewSet

# warnings.filterwarnings(action="ignore")


# class UserViewSetTest(TestCase):
#     test_fixtures = [
#         "users",
#     ]

#     fixtures = ["/app/fixtures/users.json"]
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = User.objects.create_superuser(username="scooby", password="zoinks", email="scooby@test.com")

#     def test_user_viewset(self):
#         request = self.factory.get(
#             "/api/users",
#         )
#         force_authenticate(request, user=self.user)
#         response = UserViewSet.as_view({"get": "list"})(request)
#         self.assertEqual(response.data["results"][0]["username"], "alefew")
#         self.assertEqual(response.status_code, HTTPStatus.OK._value_)

#     def test_user_create(self):
#         data = json.dumps(
#             {
#                 "username": "abel",
#                 "email": "abel@mailinator.com",
#                 "password": "PASSabc123",
#                 "is_staff": True,
#                 "is_superuser": True,
#             }
#         )
#         client = APIClient()
#         client.force_authenticate(user=self.user)
#         response = client.post("/api/users", data=data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.CREATED._value_)
#         self.assertEqual(response.data["email"], "abel@mailinator.com")

#     def test_user_destroy(self):
#         client = APIClient()
#         client.force_authenticate(user=self.user)
#         # check delete using existing user
#         response = client.delete("/api/users/{}".format(8))
#         self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT._value_)

#         # check delete using non existing user
#         response = client.delete("/api/users/{}".format(800))
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND._value_)


# class StaffViewSetTest(TestCase):
#     test_fixtures = [
#         "users",
#         "staffs",
#     ]

#     fixtures = ["/app/fixtures/users.json", "/app/fixtures/staffs.json"]

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = User.objects.create_superuser(username="scooby", password="zoinks", email="scooby@test.com")

#     def test_staff_viewset(self):
#         request = self.factory.get(
#             "/api/staffs",
#         )
#         force_authenticate(request, user=self.user)
#         response = StaffViewSet.as_view({"get": "list"})(request)
#         self.assertEqual(response.data["results"][0]["username"], "kabila")
#         self.assertEqual(response.status_code, HTTPStatus.OK._value_)

#     def test_staff_create(self):
#         existing_data = json.dumps(
#             {"username": "yosef", "email": "yosef@mailinator.com", "first_name": "yosef", "last_name": "yosef"}
#         )
#         new_data = json.dumps(
#             {"username": "hlina", "email": "hlina@mailinator.com", "first_name": "hlina", "last_name": "hlina"}
#         )
#         client = APIClient()
#         client.force_authenticate(user=self.user)
#         # test with existing username
#         response = client.post("/api/staffs", data=existing_data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST._value_)
#         self.assertEqual(response.data["username"][0], "user with this username already exists.")

#         # test with new username
#         response = client.post("/api/staffs", data=new_data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.OK._value_)
#         self.assertEqual(response.data["username"], "hlina")

#     def test_staff_destroy(self):
#         client = APIClient()
#         client.force_authenticate(user=self.user)
#         # check delete using existing staffs
#         response = client.delete("/api/staffs/{}".format(6))
#         self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT._value_)

#         # check delete using non existing staffs
#         response = client.delete("/api/staffs/{}".format(800))
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND._value_)

#     def test_staff_update(self):
#         data = json.dumps(
#             {
#                 "username": "yosefe",
#                 "email": "yosefe@mailinator.com",
#                 "first_name": "yosefe",
#                 "last_name": "yosefe",
#                 "user": 7,
#             }
#         )
#         client = APIClient()
#         client.force_authenticate(user=self.user)
#         # check update using non existing id
#         response = client.put("/api/staffs/{}".format(600), data=data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND._value_)

#         # check update using existing id
#         response = client.put("/api/staffs/{}".format(7), data=data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.OK._value_)
#         self.assertEqual(response.data["username"], "yosefe")


# class StudentModelViewSetTest(TestCase):
#     test_fixtures = [
#         "users",
#         "batches",
#         "students",
#     ]

#     fixtures = [
#         "/app/fixtures/users.json",
#         "/app/fixtures/batches.json",
#         "/app/fixtures/students.json",
#     ]

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = User.objects.create_superuser(
#             username="scooby",
#             password="zoinks",
#             email="scooby@test.com",
#         )

#     def test_student_viewset(self):
#         request = self.factory.get(
#             "/api/students",
#         )
#         force_authenticate(request, user=self.user)
#         response = StudentModelViewSet.as_view({"get": "list"})(request)
#         self.assertEqual(response.data[0]["username"], "username1")
#         self.assertEqual(response.status_code, HTTPStatus.OK._value_)

#     def test_student_create(self):
#         existing_data = json.dumps(
#             {
#                 "username": "username101",
#                 "email": "stu101@mailinator.com",
#                 "batch": "2014",
#                 "first_name": "zemenu",
#                 "last_name": "tesema",
#             }
#         )
#         new_data = json.dumps(
#             {
#                 "username": "student1000",
#                 "email": "student1000@gmail.com",
#                 "batch": "2014",
#                 "first_name": "zemenu",
#                 "last_name": "tesema",
#             }
#         )
#         client = APIClient()
#         client.force_authenticate(user=self.user)
#         # test with existing username
#         response = client.post("/api/students", data=existing_data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST._value_)
#         self.assertEqual(response.data["username"][0], "user with this username already exists.")

#         # test with new username
#         response = client.post("/api/students", data=new_data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.OK._value_)
#         self.assertEqual(response.data["username"], "student1000")

#     def test_student_update(self):
#         data = json.dumps(
#             {
#                 "username": "username49",
#                 "email": "stu49@mailinator.com",
#                 "batch": "2014",
#                 "first_name": "zemenup",
#                 "last_name": "tesema",
#                 "user": 184,
#             }
#         )
#         client = APIClient()
#         client.force_authenticate(user=self.user)
#         # check update using non existing id
#         response = client.put("/api/students/{}".format(600), data=data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND._value_)

#         # check update using existing id
#         response = client.put("/api/students/{}".format(147), data=data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.OK._value_)
#         self.assertEqual(response.data["first_name"], "zemenup")

# class ExaminerModelViewSetTest(TransactionTestCase):
#     test_fixtures = [
#         "users",
#         "batches",
#         "staffs",
#         "coordinators",
#     ]

#     fixtures = [
#         "/app/fixtures/users.json",
#         "/app/fixtures/batches.json",
#         "/app/fixtures/staffs.json",
#         "/app/fixtures/coordinators.json",
#     ]

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = User.objects.get(username="alefew")

#     def test_coordinator_viewset(self):
#         request = self.factory.get(
#             "/api/coordinators",
#         )
#         force_authenticate(request, user=self.user)
#         response = CoordinatorModelViewSet.as_view({"get": "list"})(request)
#         self.assertEqual(response.data["results"][0]["user"], "kabila")
#         self.assertEqual(response.status_code, HTTPStatus.OK._value_)

#     def test_coordinator_create(self):
#         non_existing_coordinator_data =json.dumps( {
#             "batch":"2014",
#             "user":"yosefa"
#         })
#         existing_data = json.dumps({
#             "batch":"2014",
#             "user":"yosef"
#         })
#         client = APIClient()
#         client.force_authenticate(user=self.user)
#         # test with coordinator that dont exists
#         response = client.post("/api/coordinators", data=non_existing_coordinator_data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST._value_)
#         self.assertEqual(response.data['user'][0], 'Object with username=yosefa does not exist.')

#         # test with existing data
#         response = client.post("/api/coordinators", data=existing_data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.CREATED._value_)
#         self.assertEqual(response.data["user"], "yosef")

#     def test_coordinator_destroy(self):
#         client = APIClient()
#         client.force_authenticate(user=self.user)

#         # check delete using existing coordinator id
#         response = client.delete("/api/coordinators/{}".format(9))
#         self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT._value_)

#         # check delete using non existing coordinator id
#         response = client.delete("/api/coordinators/{}".format(260))
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND._value_)
