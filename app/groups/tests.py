# import json
# import warnings
# from http import HTTPStatus

# from core.models import User
# from django.test import RequestFactory, TransactionTestCase
# from rest_framework.test import APIClient, force_authenticate

# from groups.views import GroupsModelViewSet, AdvisorModelViewSet, ExaminerModelViewSet, MemberModelViewSet

# warnings.filterwarnings(action="ignore")


# class GroupsModelViewSetTest(TransactionTestCase):
#     test_fixtures = [
#         "users",
#         "batches",
#         "students",
#         "staffs",
#         "coordinators",
#         "advisors",
#         "examiners",
#         "groups",
#     ]

#     fixtures = [
#         "/app/fixtures/users.json",
#         "/app/fixtures/batches.json",
#         "/app/fixtures/students.json",
#         "/app/fixtures/staffs.json",
#         "/app/fixtures/coordinators.json",
#         "/app/fixtures/advisors.json",
#         "/app/fixtures/examiners.json",
#         "/app/fixtures/groups.json",
#     ]

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = User.objects.get(username="kabila")

#     def test_group_viewset(self):
#         request = self.factory.get(
#             "/api/groups",
#         )
#         force_authenticate(request, user=self.user)
#         response = AdvisorModelViewSet.as_view({"get": "list"})(request)
#         self.assertEqual(response.data["results"][0]["group_name"], "Group 2")
#         self.assertEqual(response.status_code, HTTPStatus.OK._value_)

#     def test_group_create(self):
#         existing_group_name_data = json.dumps(
#             {
#                 "group_name": "Group 2",
#                 "group_members": [
#                     "username102",
#                     "username103",
#                     "username104",
#                 ],
#             }
#         )

#         new_data = json.dumps(
#             {
#                 "group_name": "Group 50",
#                 "group_members": [
#                     "username102",
#                     "username103",
#                     "username104",
#                 ],
#             },
#         )
#         self.user = User.objects.get(
#             username="username100",
#         )
#         client = APIClient()
#         client.force_authenticate(user=self.user)
#         # test with group name that already exists
#         response = client.post("/api/groups", data=existing_group_name_data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST._value_)
#         self.assertEqual(response.data["error"], "group name already exists")

#         # test with  new group
#         response = client.post("/api/groups", data=new_data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.CREATED._value_)
#         self.assertEqual(response.data["group_name"], "Group 50")

#     def test_group_destroy(self):
#         client = APIClient()
#         self.user = User.objects.get(username="kabila")
#         client.force_authenticate(user=self.user)

#         # check delete using existing group id
#         response = client.delete("/api/groups/{}".format(26))
#         self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT._value_)

#         # check delete using non existing group id
#         response = client.delete("/api/groups/{}".format(260))
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND._value_)

#     # def test_group_update(self):
#     #     data = json.dumps(
#     #         {
#     #             "group_name": "Group 2w",
#     #             "group_members": [
#     #                 "username36",
#     #                 "username37",
#     #                 "username38",
#     #             ]
#     #         }
#     #     )
#     #     client = APIClient()
#     #     client.force_authenticate(user=self.user)
#     #     # check update using non existing id
#     #     response = client.put("/api/groups/{}".format(600), data=data, content_type="application/json")
#     #     self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND._value_)

#     #     # check update using existing id
#     #     response = client.put("/api/groups/{}".format(26), data=data, content_type="application/json")
#     #     print(response.data)
#     #     self.assertEqual(response.status_code, HTTPStatus.OK._value_)
#     #     self.assertEqual(response.data["username"], "yosefe")


# class AdvisorModelViewSetViewSetTest(TransactionTestCase):
#     test_fixtures = [
#         "users",
#         "batches",
#         "students",
#         "staffs",
#         "coordinators",
#         "advisors",
#         "examiners",
#         "groups",
#     ]

#     fixtures = [
#         "/app/fixtures/users.json",
#         "/app/fixtures/batches.json",
#         "/app/fixtures/students.json",
#         "/app/fixtures/staffs.json",
#         "/app/fixtures/coordinators.json",
#         "/app/fixtures/advisors.json",
#         "/app/fixtures/examiners.json",
#         "/app/fixtures/groups.json",
#     ]

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = User.objects.get(username="kabila")

#     def test_advisor_viewset(self):
#         request = self.factory.get(
#             "/api/advisors",
#         )
#         force_authenticate(request, user=self.user)
#         response = AdvisorModelViewSet.as_view({"get": "list"})(request)
#         self.assertEqual(response.data["results"][0]["username"], "kabila")
#         self.assertEqual(response.status_code, HTTPStatus.OK._value_)

#     def test_advisor_create(self):
#         non_existing_advisor_data =json.dumps( {
#             "group":26,
#             "advisor":"yosefa"
#         })
#         existing_data = json.dumps({
#             "group":26,
#             "advisor":"yosef"
#         })
#         client = APIClient()
#         client.force_authenticate(user=self.user)
#         # test with advisor that dont exists
#         response = client.post("/api/advisors", data=non_existing_advisor_data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST._value_)
#         self.assertEqual(response.data['advisor'][0], 'Object with username=yosefa does not exist.')

#         # test with existing data
#         response = client.post("/api/advisors", data=existing_data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.CREATED._value_)
#         self.assertEqual(response.data["advisor"], "yosef")

#     def test_advisor_destroy(self):
#         client = APIClient()
#         client.force_authenticate(user=self.user)

#         # check delete using existing advisor id
#         response = client.delete("/api/advisors/{}".format(1))
#         self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT._value_)

#         # check delete using non existing advisor id
#         response = client.delete("/api/advisors/{}".format(260))
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND._value_)



# class ExaminerModelViewSetTest(TransactionTestCase):
#     test_fixtures = [
#         "users",
#         "batches",
#         "students",
#         "staffs",
#         "coordinators",
#         "advisors",
#         "examiners",
#         "groups",
#     ]

#     fixtures = [
#         "/app/fixtures/users.json",
#         "/app/fixtures/batches.json",
#         "/app/fixtures/students.json",
#         "/app/fixtures/staffs.json",
#         "/app/fixtures/coordinators.json",
#         "/app/fixtures/advisors.json",
#         "/app/fixtures/examiners.json",
#         "/app/fixtures/groups.json",
#     ]

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = User.objects.get(username="kabila")

#     def test_examiner_viewset(self):
#         request = self.factory.get(
#             "/api/examiners",
#         )
#         force_authenticate(request, user=self.user)
#         response = ExaminerModelViewSet.as_view({"get": "list"})(request)
#         self.assertEqual(response.data["results"][0]["username"], "enderias")
#         self.assertEqual(response.status_code, HTTPStatus.OK._value_)

#     def test_examiner_create(self):
#         non_existing_examiner_data =json.dumps( {
#             "group":26,
#             "examiner":"yosefa"
#         })
#         existing_data = json.dumps({
#             "group":26,
#             "examiner":"yosef"
#         })
#         client = APIClient()
#         client.force_authenticate(user=self.user)
#         # test with examiner that dont exists
#         response = client.post("/api/examiners", data=non_existing_examiner_data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST._value_)
#         self.assertEqual(response.data['examiner'][0], 'Object with username=yosefa does not exist.')

#         # test with existing data
#         response = client.post("/api/examiners", data=existing_data, content_type="application/json")
#         self.assertEqual(response.status_code, HTTPStatus.CREATED._value_)
#         self.assertEqual(response.data["examiner"], "yosef")

#     def test_examiner_destroy(self):
#         client = APIClient()
#         client.force_authenticate(user=self.user)

#         # check delete using existing examiner id
#         response = client.delete("/api/examiners/{}".format(1))
#         self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT._value_)

#         # check delete using non existing examiner id
#         response = client.delete("/api/examiners/{}".format(260))
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND._value_)











































            # member_already_joined_data = json.dumps(
        #     {
        #         "group_name": "Group 1",
        #         "group_members": [
        #             "username36",
        #             "username37",
        #             "username38",
        #         ]
        #     }
        # )