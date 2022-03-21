import csv

from django.contrib.auth.base_user import BaseUserManager
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import APIView, ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from core.models import Batch, Student, User
from core.permissions import IsAdmin, IsAdminOrReadOnly, IsStaff, IsStudent
from users.serializers import (AuthTokenSerializer, BatchSerializer,
                               StaffRegistrationSerializer, StaffSerializer,
                               StudentRegistrationSerializer,
                               StudentSerializer, UserSerializer)

fs = FileSystemStorage(location="tmp/")


class BatchModelViewSet(ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    pagination_class = None


class StaffRegistrationView(generics.GenericAPIView):
    serializer_class = StaffRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
        staff_serialize = StaffSerializer(staff)
        data = staff_serialize.data

        return Response(
            {
                "user_info": data,
                "token": Token.objects.get(user=staff.user).key,
                "message": "account created successfully",
            }
        )


class StudentRegistrationView(generics.GenericAPIView):
    serializer_class = StudentRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        student_serialize = StudentSerializer(student)
        data = student_serialize.data

        return Response(
            {
                "user_info": data,
                "token": Token.objects.get(user=student.user).key,
                "message": "account created successfully",
            }
        )


class CreateTokenView(ObtainAuthToken):
    """Create a new token for user"""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user_id": user.pk, "is_staff": user.is_staff}
        )

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class LogoutView(APIView):
    def post(self, request, format=None):
        request.auth.delete()
        return Response(status=status.HTTP_200_OK)


class StudentsOnlyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated & IsStudent]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return Student.objects.select_related("user", "batch")


class StaffsOnlyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated & IsStaff]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class StudentViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Product.
    """

    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[IsAdmin],
        url_path="(?P<batch>[^/.]+)",
    )
    def registration(self, request, batch):
        print("-----------hello---")
        """Register Students from CSV"""
        print(batch)
        batch = get_object_or_404(Batch, pk=batch)
        if not batch.is_active:
            return Response("batch is inactive", status=status.HTTP_400_BAD_REQUEST)
        file = request.FILES["file"]

        content = file.read()
        file_content = ContentFile(content)
        file_name = fs.save("_tmp.csv", file_content)
        tmp_file = fs.path(file_name)

        csv_file = open(tmp_file, errors="ignore")
        reader = csv.reader(csv_file)
        next(reader)

        student_list = []
        for id_, row in enumerate(reader):
            (username, email, firstname, lastname) = row
            user = User(username=username, email=email)
            batch_model = Batch(name=batch)
            password = BaseUserManager().make_random_password()
            user.set_password(password)
            user.save()

            student_list.append(Student(user=user, batch=batch_model))

        Student.objects.bulk_create(student_list)
        fs.delete(file_name)

        return Response("Successfully upload the data")


'''
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticate user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retreive and return authenticate user"""
        return self.request.user
'''
