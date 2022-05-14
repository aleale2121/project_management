import csv
from constants.constants import MODEL_CREATION_FAILED, MODEL_DELETE_FAILED, MODEL_RECORD_NOT_FOUND, MODEL_UPDATE_FAILED
from  pkg.util import error_response
from core.models import Batch, Coordinator, Staff, Student, User
from core.permissions import IsAdmin, IsAdminOrReadOnly
from django.db import transaction
from django.contrib.auth.base_user import BaseUserManager
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from .tasks import send_email_task,send_email_for_student
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

            msg = password+" is your password for site repository management application,don't share it for any one else!"
            ctx_list.append(
                {
                    "username": username,
                    "first_name": firstname,
                    "last_name": lastname,
                    "email": email,
                    "subject": "Dear "+firstname+" "+lastname,
                    "msg": msg,
                }
            )

        from_email = "yidegaait2010@gmail.com"
        email_tuple = tuple()
        for i in ctx_list:
            email_tuple = email_tuple + ((i["subject"], i["msg"], from_email, [i["email"]]),)
        fs.delete(tmp_file)
        # email_res = send_mass_mail((email_tuple), fail_silently=False)
        try:
            Student.objects.bulk_create(student_list)
            res=send_email_task.delay(email_tuple)
            if res == None:
                return Response({"message":"Students registered  successfully"})
            else:
                return Response({"message:":"Error while emailing"})

        except Exception as e:
            if e:
                print("error while creating new  stuents ",e)
                return Response({ "Error Has Occured"})

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
    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[IsAdmin],
        url_path="add-new",
    )
    def add_student(self,request,pk=None):
        form_data=request.data
        student_id=form_data["user_id"]
        password = BaseUserManager().make_random_password()
        student_obj=None
        if User.objects.get(id=student_id).exists() and not Student.objects.get(user=User.objects.get(id=student_id)):
            batch_obj=None
            try:
                batch_obj = Batch.objects.get(name=form_data["batch"])
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "Batch")
                return Response(res, content_type="application/json")

        try:
            usr=User.objects.get(id=student_id)
            subject='Dear '+form_data["first_name"] +" "+form_data["last_name"]
            message=password +' is your new passsword!'
            fromMail='yidegaait2010@gmail.com'
            toArr=[usr.email]
            student_obj = Student.objects.create(
                user=User.objects.get(id=student_id),
                batch=batch_obj,
                first_name=form_data["first_name"],
                last_name=form_data["first_name"]
            )
                
            send_email_for_student.delay(subject,message,fromMail,toArr)
            serializer = StudentSerializer(student_obj)
            return Response(serializer.data)
        except Exception as e:
            if e:
                print("error while sending message ",e)
                return Response({ "Error Has Occured while adding students!"})
            
    @action(
        detail=True,
        methods=["DELETE"],
        permission_classes=[IsAdmin],
        url_path="drop",
    )
    def drop_student(self,request,pk=None):
        if Student.objects.get(id=pk).exists():
            student_obj=Student.objects.get(id=pk).delete()
            return Response({"message":f"Student with id {student_obj.user} successfuly deleted!" })
        else:
            res = error_response(request, MODEL_DELETE_FAILED, "Student")
            return Response(res, content_type="application/json")

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[IsAdmin],
        url_path="email/reset",
    )
    def rest_email(self,request):
        form_data=request.data
        password = User.objects.make_random_password()

        if User.objects.get(username=form_data["username"]).exists():
            user_obj=User.objects.filter(username=form_data["username"])
            user_obj.email=form_data['email']
            user_obj.set_password(password)
            user_obj.save(update_fields=['password'])
            body=password +" is your new password."
            from_email ="alefewyimer2@gmail.com"
            to_email=form_data['email']
            subject='Email and Passsword Reset'
            toArr=[to_email]
            send_email_for_student.delay(subject,body,from_email,toArr)
            if res == None:
                return Response({"message":f"Student with username {form_data['username']} successfuly updated!" })
            else:
                return Response({"message":"email not sent to "+form_data['first_name']+" "+form_data['last_name']})
        else:
            res = error_response(request, MODEL_UPDATE_FAILED, "Student")
            return Response(res, content_type="application/json")




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
