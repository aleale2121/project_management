import csv

from core.models import Advisor, Batch, Coordinator, Group, Member, Staff, Student, User
from core.permissions import IsAdmin, IsAdminOrReadOnly, IsStaff
from django.contrib.auth.base_user import BaseUserManager
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mass_mail
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from groups.serializers import ReadGroupSerializer
from rest_framework import authentication, generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import APIView, ObtainAuthToken
from rest_framework.decorators import action, api_view, permission_classes
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

        joinedGroup = None
        try:
            member = Member.objects.get(member=user)
            group = ReadGroupSerializer(member.group)
            if group != None:
                joinedGroup = group.data
        except Member.DoesNotExist:
            pass
        advisor_to = []
        examiner_to = []
        if active_batch != None:
            try:
                advisor_to = ReadGroupSerializer(
                    Group.objects.filter(batch=active_batch).filter(advisors__advisor__exact=user), many=True
                )
                examiner_to = ReadGroupSerializer(
                    Group.objects.filter(batch=active_batch).filter(examiners__examiner__exact=user), many=True
                )

            except Batch.DoesNotExist:
                pass

        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "is_superadmin": user.is_superuser,
                "is_staff": user.is_staff,
                "is_coordinator": is_coordinator,
                "is_student": user.is_student,
                "group": joinedGroup,
                "advisor_to": advisor_to.data,
                "examiner_to": examiner_to.data,
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


class UserViewSet(ModelViewSet):
    """Manage the authenticated user"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)


class LogoutView(APIView):
    def post(self, request, format=None):
        request.auth.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsStaff,))
def advisor_groups_view(request, format=None):
    user = request.user
    active_batch = None
    try:
        active_batch = Batch.objects.get(is_active=True)
    except Batch.DoesNotExist:
        pass

    advisor_to = []
    if active_batch != None:
        try:
            advisor_to = ReadGroupSerializer(
                Group.objects.filter(batch=active_batch).filter(advisors__advisor__exact=user),
                many=True,
            )

        except Batch.DoesNotExist:
            pass
    return Response(((advisor_to.data)))


@api_view(["GET"])
@permission_classes((IsStaff,))
def examiner_groups_view(request, format=None):
    user = request.user
    active_batch = None
    try:
        active_batch = Batch.objects.get(is_active=True)
    except Batch.DoesNotExist:
        pass

    examiner_to = []
    if active_batch != None:
        try:
            examiner_to = ReadGroupSerializer(
                Group.objects.filter(batch=active_batch).filter(examiners__examiner__exact=user),
                many=True,
            )

        except Batch.DoesNotExist:
            pass
    return Response(((examiner_to.data)))


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
        staff_serialize = StaffSerializerTwo(staff)
        data = staff_serialize.data

        return Response(data)

    def update(self, request, *args, **kwargs):
        staff = get_object_or_404(Staff, pk=kwargs["pk"])
        serializer = StaffRegistrationSerializer(
            staff.user,
            data=request.data,
            context={"request": request, "view": self},
        )
        serializer.is_valid(raise_exception=True)
        staff = serializer.updateStaff()
        staff_serialize = StaffSerializerTwo(staff)
        data = staff_serialize.data
        return Response(data)

class StudentRegistrationModelViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentRegistrationSerializer

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
        print(request)
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
            msg = "Your SiTE Project Repository password is " + password
            ctx_list.append(
                {
                    "username": username,
                    "first_name": firstname,
                    "last_name": lastname,
                    "email": email,
                    "subject": "SiTE Project Repository Password",
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

class StudentModelViewSet(ModelViewSet):

    filterset_fields = [
        "batch",
    ]
    queryset = Student.objects.all()
    permission_classes = [
        IsAdminOrReadOnly,
    ]

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
            msg = "Your SiTE Project Repository password is " + password
            ctx_list.append(
                {
                    "username": username,
                    "first_name": firstname,
                    "last_name": lastname,
                    "email": email,
                    "subject": "SiTE Project Repository Password",
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
        student_serialize = StudentSerializerTwo(student)
        data = student_serialize.data

        return Response(data)

    def update(self, request, *args, **kwargs):
        student = get_object_or_404(Student, pk=kwargs["pk"])
        serializer = StudentRegistrationSerializer(
            student.user,
            data=request.data,
            context={"request": request, "view": self},
        )
        serializer.is_valid(raise_exception=True)
        get_object_or_404(Batch, name=request.data["batch"])
        student = serializer.updateStudent()
        student_serialize = StudentSerializerTwo(student)
        data = student_serialize.data
        return Response(data)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return StudentSerializerTwo
        return StudentRegistrationSerializer

    def list(self, request, *args, **kwargs):
        all = None
        batch = None
        try:
            all = request.GET["all"]
        except MultiValueDictKeyError:
            pass

        try:
            batch = request.GET["batch"]
        except MultiValueDictKeyError:
            pass

        query = Student.objects.all()
        if batch != None:
            query = query.filter(batch="" + batch)
        if all == "False":
            query = query.exclude(
                user__in=User.objects.filter(
                    members__in=Member.objects.all(),
                )
            )

        serializer = StudentSerializerTwo(query, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Student.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


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
