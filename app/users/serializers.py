from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.models import Batch, Staff, Student, User


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ("name", "is_active")
        read_only_fields = ["is_active"]

    def create(self, validated_data):
        Batch.objects.update(is_active=False)
        # batch = Batch(
        #     name=validated_data['name'],
        #     is_active=True
        # )
        return Batch.objects.create(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "is_staff", "is_superuser")


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    user = UserSerializer()

    class Meta:
        model = Student
        fields = ("user", "batch")


class StaffSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    user = UserSerializer()

    class Meta:
        model = Student
        fields = ("user",)


class WriteStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("user_id", "username", "email", "password")


class StaffRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def save(self, **kwargs):
        user = User(
            username=self.validated_data["username"], email=self.validated_data["email"]
        )
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
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    batch = serializers.SlugRelatedField(
        slug_field="name", queryset=Batch.objects.all()
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2", "batch"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def save(self, **kwargs):
        user = User(
            username=self.validated_data["username"], email=self.validated_data["email"]
        )
        password = (self.validated_data["password"],)
        password2 = (self.validated_data["password2"],)
        if password != password2:
            raise serializers.ValidationError({"error": "password don't match"})
        user.set_password(password[0])
        user.is_superuser = False
        user.is_student = True
        user.save()
        student = Student.objects.create(user=user, batch=self.validated_data["batch"])
        return student


'''
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    class Meta:
        model = get_user_model()
        fields = ('username','email', 'password', 'name')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5
            }
        }

    def create(self, validate_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validate_data)

    def update(self, instance, validate_data):
        """Update a user, setting the password correctly and return it"""
        password = validate_data.pop('password', None)
        user = super().update(instance, validate_data)

        if password:
            user.set_password(password)
        user.save()

        return user


'''


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authenticate object"""

    username = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        username = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"), username=username, password=password
        )

        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authentication")

        attrs["user"] = user
        return attrs
