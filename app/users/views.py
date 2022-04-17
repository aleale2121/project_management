import csv

from core.models import Batch, Coordinator, Staff, Student, User
from core.permissions import IsAdmin, IsAdminOrReadOnly
from django.contrib.auth.base_user import BaseUserManager
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage, send_mail, send_mass_mail
from django.shortcuts import get_object_or_404
from rest_framework import authentication, generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import APIView, ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from users.serializers import (
    AdminRegistrationSerializer,
    AuthTokenSerializer,
    BatchSerializer,
    CoordinatorSerialzer,
    StaffRegistrationSerializer,
    StaffSerializer,
    StaffSerializerTwo,
    StudentRegistrationSerializer,
    StudentSerializer,
    StudentSerializerTwo,
    UserSerializer,
)

fs = FileSystemStorage(location="tmp/")


class BatchModelViewSet(ModelViewSet):

    permission_classes = (IsAdminOrReadOnly,)
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    pagination_class = None


class CreateTokenView(ObtainAuthToken):
    """Create a new token for user"""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        active_batch = None
        try:
            active_batch = Batch.objects.get(is_active=True)
        except Batch.DoesNotExist:
            pass

        coordinator_history = None
        is_coordinator = False

        if active_batch != None:
            try:
                coordinator_history = Coordinator.objects.get(user=user, batch=active_batch)
            except Coordinator.DoesNotExist:
                pass
        if coordinator_history != None:
            is_coordinator = True

        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "is_superadmin": user.is_superuser,
                "is_staff": user.is_staff,
                "is_coordinator": is_coordinator,
                "is_student": user.is_student,
            }
        )

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authentication user"""
        return self.request.user


class LogoutView(APIView):
    def post(self, request, format=None):
        request.auth.delete()
        return Response(status=status.HTTP_200_OK)


class AdminViewSet(ModelViewSet):
    queryset = User.objects.filter(is_superuser=True)

    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = AdminRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin = serializer.save()
        admin_serialize = UserSerializer(admin)
        data = admin_serialize.data

        return Response(
            {
                "user_info": data,
                "message": "admin account created successfully",
            }
        )


class StaffViewSet(ModelViewSet):
    queryset = Staff.objects.all()

    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return StaffSerializerTwo
        return StaffSerializer

    def create(self, request, *args, **kwargs):
        serializer = StaffRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
        staff_serialize = StaffSerializer(staff)
        data = staff_serialize.data

        return Response(
            {
                "user_info": data,
                "message": "account created successfully",
            }
        )


class StudentViewSet(viewsets.ModelViewSet):

    filterset_fields = [
        "batch",
    ]

    queryset = Student.objects.all()
    serializer_class = StudentSerializerTwo

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[IsAdmin],
        url_path="(?P<batch>[^/.]+)",
    )
    def registration(self, request, batch):
        """Register Students from CSV"""
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
        ctx_list = []
        for id_, row in enumerate(reader):
            (username, email, firstname, lastname) = row
            user = User(username=username, email=email)
            batch_model = Batch(name=batch)
            password = BaseUserManager().make_random_password()
            user.is_student = True
            user.set_password(password)
            user.save()

            student_list.append(
                Student(
                    user=user,
                    batch=batch_model,
                    first_name=firstname,
                    last_name=lastname,
                )
            )
            msg = "your SiTE Project Repository password is " + password
            ctx_list.append(
                {
                    "username": username,
                    "first_name": firstname,
                    "last_name": lastname,
                    "email": email,
                    "subject": "SiTE Repository Password announcement",
                    "msg": msg,
                }
            )

        from_email = "alefewyimer2@gmail.com"
        email_tuple = tuple()

        for i in ctx_list:
            email_tuple = email_tuple + ((i["subject"], i["msg"], from_email, [i["email"]]),)

        fs.delete(tmp_file)
        email_res = send_mass_mail((email_tuple), fail_silently=False)
        Student.objects.bulk_create(student_list)
        return Response("Students registered  successfully")

    def create(self, request, *args, **kwargs):
        serializer = StudentRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        student_serialize = StudentSerializer(student)
        data = student_serialize.data

        return Response(
            {
                "user_info": data,
                "message": "account created successfully",
            }
        )


class CoordinatorModelViewSet(ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = CoordinatorSerialzer

    def get_queryset(self):
        return Coordinator.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Coordinator.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
