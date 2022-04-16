from core.models import Batch, Coordinator, Member, Staff, Student, User
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authenticate object"""

    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)

    def validate(self, attrs):
        """Validate and authenticate the user"""
        username = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(request=self.context.get("request"), username=username, password=password)

        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authentication")

        attrs["user"] = user
        return attrs


class BatchSerializer(serializers.ModelSerializer):
    """Serializer for the batch object"""

    class Meta:
        model = Batch
        fields = ("name", "is_active")
        read_only_fields = ["is_active"]

    def create(self, validated_data):
        Batch.objects.update(is_active=False)
        return Batch.objects.create(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "is_staff", "is_superuser")


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    user = UserSerializer()
    batch = BatchSerializer()

    class Meta:
        model = Student
        fields = ("user", "batch")


class StudentSerializerTwo(serializers.ModelSerializer):
    """Serializer for the student object"""

    username = SerializerMethodField()
    email = SerializerMethodField()
    batch = SerializerMethodField()

    class Meta:
        model = Student
        fields = "__all__"

    def get_username(self, obj):
        return UserSerializer(obj.user).data["username"]

    def get_email(self, obj):
        return UserSerializer(obj.user).data["email"]

    def get_batch(self, obj):
        return BatchSerializer(obj.batch).data["name"]


class StaffSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    user = UserSerializer()

    class Meta:
        model = Staff
        fields = ("user",)


class StaffSerializerTwo(serializers.ModelSerializer):
    """Serializer for the staff object"""

    username = SerializerMethodField()
    email = SerializerMethodField()

    class Meta:
        model = Staff
        fields = "__all__"

    def get_username(self, obj):
        return UserSerializer(obj.user).data["username"]

    def get_email(self, obj):
        return UserSerializer(obj.user).data["email"]


class StaffSerializerThree(serializers.ModelSerializer):
    """Serializer for the staff object"""

    username = SerializerMethodField()
    email = SerializerMethodField()

    class Meta:
        model = Staff
        fields = "__all__"

    def get_username(self, obj):
        return UserSerializer(obj.user).data["username"]

    def get_email(self, obj):
        return UserSerializer(obj.user).data["email"]


class AdminRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for the admin object"""

    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def save(self, **kwargs):
        user = User(username=self.validated_data["username"], email=self.validated_data["email"])
        password = (self.validated_data["password"],)
        password2 = (self.validated_data["password2"],)
        if password != password2:
            raise serializers.ValidationError({"error": "password don't match"})
        user.set_password(password[0])
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class StaffRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for the staff registration"""

    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def save(self, **kwargs):
        user = User(username=self.validated_data["username"], email=self.validated_data["email"])
        password = (self.validated_data["password"],)
        password2 = (self.validated_data["password2"],)
        if password != password2:
            raise serializers.ValidationError({"error": "password don't match"})
        user.set_password(password[0])
        user.is_superuser = False
        user.is_staff = True
        user.save()
        staff = Staff.objects.create(user=user)
        return staff


class StudentRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for the student registration"""

    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    batch = serializers.SlugRelatedField(slug_field="name", queryset=Batch.objects.all())

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2", "batch"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def save(self, **kwargs):
        user = User(username=self.validated_data["username"], email=self.validated_data["email"])
        password = (self.validated_data["password"],)
        password2 = (self.validated_data["password2"],)
        if password != password2:
            raise serializers.ValidationError({"error": "password don't match"})
        user.set_password(password[0])
        user.is_superuser = False
        user.is_student = True
        user.save()
        student = Student.objects.create(
            user=user,
            batch=self.validated_data["batch"],
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
        )
        return student


class CoordinatorSerialzer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())
    batch = serializers.SlugRelatedField(slug_field="name", queryset=Batch.objects.all())

    class Meta:
        model = Coordinator
        fields = (
            "batch",
            "user",
        )
