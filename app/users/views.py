import csv

# from dynamic_preferences.registries import global_preferences_registry
from constants.constants import (
    MODEL_ALREADY_EXIST,
    MODEL_DELETE_FAILED,
    MODEL_PARAM_MISSED,
    MODEL_RECORD_NOT_FOUND,
    MODEL_UPDATE_FAILED,
)
from core.models import Batch, Coordinator, Group, Member, Staff, Student, User
from core.permissions import IsAdmin, IsAdminOrReadOnly, IsStaff,IsAdminAndStudent
from django.contrib.auth import authenticate
from django.contrib.auth.base_user import BaseUserManager
from rest_framework.permissions import IsAuthenticated
from django.core import mail
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail, send_mass_mail
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from groups.serializers import ReadGroupSerializer
from pkg.util import error_response
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
                ).data
                examiner_to = ReadGroupSerializer(
                    Group.objects.filter(batch=active_batch).filter(examiners__examiner__exact=user), many=True
                ).data

            except Batch.DoesNotExist:
                pass
        active_batch_resp=""
        if(active_batch!=None):
            active_batch_resp=active_batch.name
        
        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "username":user.username,
                "is_superadmin": user.is_superuser,
                "is_staff": user.is_staff,
                "is_coordinator": is_coordinator,
                "is_student": user.is_student,
                "group": joinedGroup,
                "advisor_to": advisor_to,
                "examiner_to": examiner_to,
                "active_batch":active_batch_resp,
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
    examiner_to = []
    if active_batch != None:
        try:
            advisor_to = ReadGroupSerializer(
                Group.objects.filter(batch=active_batch).filter(advisors__advisor__exact=user),
                many=True,
            ).data

        except Batch.DoesNotExist:
            pass
    return Response(((advisor_to)))


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
            ).data

        except Batch.DoesNotExist:
            pass
    return Response(((examiner_to)))


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
    permission_classes = [IsAdminOrReadOnly]

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
        file = request.FILES["file"]

        content = file.read()
        file_content = ContentFile(content)
        file_name = fs.save("_tmp.csv", file_content)
        tmp_file = fs.path(file_name)

        csv_file = open(tmp_file, errors="ignore")
        reader = csv.reader(csv_file)
        next(reader)

        student_list = []
        username_list = []
        email_list = []
        user_list = []
        from_email = "misganewendeg879@gmail.com"
        email_message_list = []
        subject = ("SiTE Project Repository Password",)

        batch_model = Batch(name=batch)
        for id_, row in enumerate(reader):
            (username, email, firstname, lastname) = row
            user = User(username=username, email=email)
            password = BaseUserManager().make_random_password()
            user.is_student = True
            user.set_password(password)
            user_list.append(user)

            msg = "SiTE Project Repository password is: " + password

            email_message_list.append(
                mail.EmailMessage(
                    subject,
                    msg,
                    from_email,
                    [email],
                ),
            )

        users_by_username = User.objects.filter(username__in=[usr.username for usr in user_list])
        if len(users_by_username) > 0:
            res = error_response(request, MODEL_ALREADY_EXIST, "One or more username in Student")
            return Response(res, content_type="application/json")

        users_by_email = User.objects.filter(email__in=[usr.email for usr in user_list])
        if len(users_by_email) > 0:
            res = error_response(request, MODEL_ALREADY_EXIST, "One or more email in Student")
            return Response(res, content_type="application/json")
        for usr in user_list:
            usr_saved = usr
            usr_saved.save()
            student_list.append(
                Student(
                    user=usr,
                    batch=batch_model,
                    first_name=firstname,
                    last_name=lastname,
                )
            )
        Student.objects.bulk_create(student_list)
        fs.delete(tmp_file)
        connection = mail.get_connection()
        connection.open()
        try:
            first_email=email_message_list.pop()
            first_email.connection=connection
            connection.send_messages(email_message_list)
        except IndexError:
            pass
        connection.close()
        return Response("Students registered  successfully")
    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[IsAdmin],
        url_path="add-new",
    )
    def add_student(self, request, pk=None):
        form_data = request.data
        student_id = form_data["user_id"]
        password = BaseUserManager().make_random_password()
        batch_obj = None
        student_obj = None
        if User.objects.get(id=student_id).exists() and not Student.objects.get(user=User.objects.get(id=student_id)):
            try:
                batch_obj = Batch.objects.get(name=form_data["batch"])
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "Batch")
                return Response(res, content_type="application/json")
        try:
            usr = User.objects.get(id=student_id)
            subject = "Dear " + form_data["first_name"] + " " + form_data["last_name"]
            message = password + " is your new passsword!"
            fromMail = "misganewendeg879@gmail.com"
            toArr = usr.email
            student_obj = Student.objects.create(
                user=User.objects.get(id=student_id),
                batch=batch_obj,
                first_name=form_data["first_name"],
                last_name=form_data["first_name"],
            )
            send_mail(
                subject,
                message,
                fromMail,
                [toArr],
                fail_silently=False,
            )
            serializer = StudentSerializer(student_obj)
            return Response(serializer.data)
        except Exception as e:
            print("error while sending message ", e)
            return Response({"message": "Error has occured while adding dropped out students!"},status=400)

    @action(
        detail=True,
        methods=["DELETE"],
        permission_classes=[IsAdmin],
        url_path="drop",
    )
    def drop_student(self, request, pk=None):
        if Student.objects.get(id=pk).exists():
            student_obj = Student.objects.get(id=pk)
            student_obj.delete()
            return Response({"message": f"Student with id {student_obj.user} successfuly deleted!"})
        else:
            res = error_response(request, MODEL_DELETE_FAILED, "Student")
            return Response(res, content_type="application/json",status=res['status_code'])

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[IsAdmin],
        url_path="email/reset",
    )
    def reset_email(self, request):
        form_data = request.data
        password = User.objects.make_random_password() 
        username=self.request.user.username 

        if User.objects.get(username=username).exists():
            user_obj = User.objects.filter(username=username)[0]
            user_obj.email = form_data["email"]  
            user_obj.set_password(password)  
            user_obj.save(update_fields=["password","email"]) 
            body = password + " is your secured new password."
            from_email = "misganewendeg879@gmail.com"
            to_email = form_data["email"]
            subject = "Email Reset"
            toArr = to_email
            send_mail(
                subject,
                body,
                from_email,
                [toArr],
                fail_silently=False,
            )
            return Response({"message": "Email successfuly reseted!"})
        else:
            res = error_response(request, MODEL_UPDATE_FAILED, "Student")
            res['message']='Unable to reset email id'
            return Response(res, content_type="application/json",status=res['status_code'])




class StudentModelViewSet(ModelViewSet):
    filterset_fields = [
        "batch",
    ]
    queryset = Student.objects.all()
    permission_classes = [
        IsAdminOrReadOnly,
    ]

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
        
        
class UserPassword(ModelViewSet):
    @action(
        detail=False,
        methods=["POST"],
        url_path="reset-password",
    )
    def reset_password(self, request):
        username = request.user.username
        form_data=request.data
        print("logged user ==>",username)
        print("form data ==>",form_data)
        if len(form_data)==0:
            res = error_response(request, MODEL_PARAM_MISSED, "Username")
            res['message']='username field is required'
            return Response(res,status=int(res['status_code']), content_type="application/json")
            
        password = User.objects.make_random_password()
        if User.objects.filter(username=username,is_superuser=True).exists():
            # user_obj = User.objects.filter(username=form_data["username"])[0]
            user_obj=None
            try:
                user_obj = User.objects.get(username=form_data["username"])
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
                res['message']='No logged user found!'
                return Response(res,status=int(res['status_code']), content_type="application/json")
            user_obj.set_password(password)  
            user_obj.save(update_fields=["password"])
            body = password + " is your secured new password."
            from_email = "misganewendeg879@gmail.com"
            to_email = user_obj.email
            subject = "Passsword Reset"
            toArr = to_email
            send_mail(
                subject,
                body,
                from_email,
                [toArr],
                fail_silently=False,
            )
            return Response({"message": f"Student with username {form_data['username']} successfuly updated!"})
        else:
            res = error_response(request, MODEL_UPDATE_FAILED, "Student")
            res['message']="You don't have enough prmission to reset password"
            return Response(res, content_type="application/json",status=res['status_code'])
        
    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[IsAuthenticated],
        url_path="change-password",   
    )
    def change_password(self, request):
        username = self.request.user.username
        credentials=request.data
        if len(credentials)==0:
            res = error_response(request, MODEL_UPDATE_FAILED, "ChangePassword")
            res['message']="Password field required. "
            return Response(res, content_type="application/json",status=res['status_code'])
        old_password=credentials['old_password'] 
        new_password=credentials['new_password']
        confirm_password=credentials['confirm_password']
        if new_password!=confirm_password:
            res = error_response(request, MODEL_UPDATE_FAILED, "ChangePassword")
            res['message']="Password not matched. "
            return Response(res, content_type="application/json",status=res['status_code'])


        user = authenticate(username=username, password=old_password)
        if user is not None: 
            user_obj = User.objects.filter(username=username)[0]
            user_obj.set_password(new_password)  
            user_obj.save(update_fields=["password"])
            body = new_password + " is your updated secured new password."
            from_email = "misganewendeg879@gmail.com"
            to_email = user_obj.email
            subject = "Passsword Change"
            toArr = to_email
            send_mail(
                subject,
                body,
                from_email,
                [toArr],
                fail_silently=False,
            )
            return Response({"message": f"{username} password successfuly updated!"})
        else:
            res = error_response(request, MODEL_UPDATE_FAILED, "Student")
            res['message']="You don't have enough prmission to reset password"
            return Response(res, content_type="application/json",status=res['status_code'])


    
    


    
    
