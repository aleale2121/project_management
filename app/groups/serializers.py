import json
from tokenize import group

import requests
from core.models import (
    Advisor,
    Batch,
    Examiner,
    Group,
    Member,
    ProjectTitle,
    Student,
    User,
)
from django.core import serializers as djSerializer
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from users.serializers import UserSerializer


class MemberSerializer(serializers.ModelSerializer):
    """Serializer for the member object"""

    class Meta:
        model = Member
        fields = "__all__"


class ReadMembersSerializer(serializers.ModelSerializer):

    username = SerializerMethodField()
    email = SerializerMethodField()
    batch = SerializerMethodField()

    class Meta:
        model = Member
        fields = ("id", "username", "email", "batch")

    def validate(self, data):
        return super().validate(data)

    def get_username(self, obj):

        return obj.member.username

    def get_email(self, obj):
        return obj.member.email

    def get_batch(self, obj):
        student = Student.objects.get(user=obj.member)
        return student.batch.name


class AdvisorSerializer(serializers.ModelSerializer):
    """Serializer for the member object"""

    advisor = UserSerializer()

    class Meta:
        model = Advisor
        fields = "__all__"


class AdvisorSerializerTwo(serializers.ModelSerializer):

    username = SerializerMethodField()
    email = SerializerMethodField()

    class Meta:
        model = Member
        fields = ("id", "username", "email")

    def validate(self, data):
        return super().validate(data)

    def get_username(self, obj):

        return obj.advisor.username

    def get_email(self, obj):
        return obj.advisor.email


class ExaminerSerializerTwo(serializers.ModelSerializer):

    username = SerializerMethodField()
    email = SerializerMethodField()

    class Meta:
        model = Member
        fields = ("id", "username", "email")

    def validate(self, data):
        return super().validate(data)

    def get_username(self, obj):

        return obj.examiner.username

    def get_email(self, obj):
        return obj.examiner.email


class ExaminerSerializer(serializers.ModelSerializer):
    """Serializer for the member object"""

    examiner = UserSerializer()

    class Meta:
        model = Examiner
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(
        max_length=25,
    )
    group_members = serializers.ListField(child=serializers.CharField(), write_only=True)
    members = MemberSerializer(many=True, read_only=True)
    batch = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )
    advisors = AdvisorSerializer(many=True, read_only=True)
    examiners = ExaminerSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ("id", "group_name", "batch", "members", "advisors", "examiners", "group_members")
        read_only_fields = ("id", "batch", "members")
        extra_kwargs = {
            "group_members": {"write_only": True},
        }

    def validate(self, data):
        current_user = self.context["request"].user
        g_members = data.get("group_members")
        g_members.append(current_user.username)
        active_batch = None
        try:
            active_batch = Batch.objects.get(is_active=True)
        except Batch.DoesNotExist:
            raise serializers.ValidationError({"error": "currently there is no active batch"})

        current_batch_groups = Group.objects.filter(batch=active_batch)
        for current_batch_group in current_batch_groups:
            group_members_list = Member.objects.filter(group=current_batch_group)
            for group_member in group_members_list:
                for g_member in g_members:
                    print(g_member)
                    if MemberSerializer(group_member).data["member"] == g_member:
                        response = ""
                        if g_member == current_user.username:
                            response = "You have already joined " + current_batch_group.group_name
                        else:
                            response = (
                                "student with username "
                                + g_member
                                + " already joined "
                                + current_batch_group.group_name
                            )
                        raise serializers.ValidationError(
                            {
                                "error": response,
                            },
                        )

        return super().validate(data)

    def create(self, validated_data):
        current_user = self.context["request"].user

        members_data = validated_data.pop("group_members")
        active_batch = None
        try:
            active_batch = Batch.objects.get(is_active=True)
        except Batch.DoesNotExist:
            raise serializers.ValidationError({"error": "currently there is no active batch"})
        student_list = []
        for member_data in members_data:
            user = None
            try:
                user = User.objects.get(username=member_data)
                try:
                    student = Student.objects.get(user=user, batch=active_batch)
                    student_list.append(user)
                except Student.DoesNotExist:
                    response = (
                        "student with username " + member_data + " is not registered for the current acadamic year"
                    )
                    raise serializers.ValidationError({"error": response})

            except User.DoesNotExist:
                response = "student with username " + member_data + " not found"
                raise serializers.ValidationError({"error": response})

        group = None
        try:
            group = Group.objects.create(group_name=self.validated_data["group_name"], batch=active_batch)
        except IntegrityError:
            raise serializers.ValidationError({"error": "group name already exists"})

        member_objects = []
        for student in student_list:
            print(student)
            member_objects.append(Member(group=group, member=student))

        Member.objects.bulk_create(member_objects)
        return group

    def update(self, instance, validated_data):
        current_user = self.context["request"].user
        view = self.context.get("view")
        group = get_object_or_404(Group.objects, pk=view.kwargs["pk"])
        batch = get_object_or_404(Batch.objects, pk=group.batch)
        if not batch.is_active:
            raise serializers.ValidationError({"error": "inactive group"})

        members_data = validated_data.pop("group_members")
        student_list = []
        for member_data in members_data:
            user = None
            try:
                user = User.objects.get(username=member_data)
                try:
                    student = Student.objects.get(user=user, batch=group.batch)
                    student_list.append(user)
                    try:
                        member = Member.objects.get(member=user)
                        if member.group.pk != group.pk:
                            response = "student with username " + member_data + " Joined another group"
                            raise serializers.ValidationError({"error": response})
                    except Member.DoesNotExist:
                        print("hello")
                except Student.DoesNotExist:
                    response = "student with username " + member_data + " is not registered for acadamic year"
                    raise serializers.ValidationError({"error": response})

            except User.DoesNotExist:
                response = "student with username " + member_data + " not found"
                raise serializers.ValidationError({"error": response})
        try:
            if group.group_name != self.validated_data["group_name"]:
                group.group_name = self.validated_data["group_name"]
                group.save()
        except IntegrityError as error:
            raise serializers.ValidationError({"error": "group name already exists"})

        Member.objects.filter(group=group).delete()
        member_objects = []
        for student in student_list:
            member_objects.append(Member(group=group, member=student))
        Member.objects.bulk_create(member_objects)
        Member.objects.get_or_create(group=group, member=student_list[len(student_list) - 1])
        return group


class ReadGroupSerializer(serializers.ModelSerializer):

    members = ReadMembersSerializer(many=True, read_only=True)
    advisors = AdvisorSerializerTwo(many=True, read_only=True)
    examiners = ExaminerSerializerTwo(many=True, read_only=True)

    class Meta:
        model = Group
        fields = (
            "id",
            "group_name",
            "batch",
            "members",
            "advisors",
            "examiners",
        )
        read_only_fields = fields


class WriteAdvisorSerialzer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    advisor = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.filter(is_staff=True))

    class Meta:
        model = Advisor

        fields = ("group", "advisor")

    def validate(self, data):
        username = data.get("advisor")
        try:
            user = User.objects.get(username=username)
            if user.is_staff == False:
                raise serializers.ValidationError("only staff members can be advisor")
        except User.DoesNotExist:
            response_message = "user with id " + username + " not found"
            raise serializers.ValidationError(response_message)
        return super().validate(data)


class ReadAdvisorSerializer(serializers.HyperlinkedModelSerializer):
    groups = ReadGroupSerializer(
        many=True,
        read_only=True,
    )
    username = SerializerMethodField()
    email = SerializerMethodField()

    class Meta:
        model = Advisor
        fields = ("id", "username", "email", "groups")
        read_only_fields = fields

    def get_username(self, obj):
        return obj.advisor.username

    def get_email(self, obj):
        return obj.advisor.email


class WriteExaminerSerialzer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    examiner = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.filter(is_staff=True))

    class Meta:
        model = Examiner
        fields = ("group", "examiner")
    def validate(self, data):
        username = data.get("examiner")
        try:
            user = User.objects.get(username=username)
            if user.is_staff == False:
                raise serializers.ValidationError("only staff members can be examiner")
        except User.DoesNotExist:
            response_message = "user with id " + username + " not found"
            raise serializers.ValidationError(response_message)
        return super().validate(data)


class ReadExaminerSerializer(serializers.ModelSerializer):
    group = GroupSerializer()

    username = SerializerMethodField()
    email = SerializerMethodField()

    class Meta:
        model = Examiner
        fields = ("id", "username", "email", "group")
        read_only_fields = fields

    def get_username(self, obj):
        return obj.examiner.username

    def get_email(self, obj):
        return obj.examiner.email


class WriteProjectTitleSerializer(serializers.ModelSerializer):
    title_name = serializers.CharField(max_length=200)
    title_description = serializers.CharField(min_length=5)
    no = serializers.ChoiceField(choices=ProjectTitle.NO_CHOICES)

    class Meta:
        model = ProjectTitle
        fields = [
            "id",
            "title_name",
            "title_description",
            "no",
            "group",
            "rejection_reason",
            "status",
        ]
        read_only_fields = ("id", "group", "rejection_reason", "status")
        extra_kwargs = {
            "title_name": {"required": True},
            "title_description": {"required": True},
            "no": {"required": True},
        }
        depth = 1

    def create(self, request, *args, **kwargs):
        view = self.context.get("view")
        new_title = ProjectTitle.objects.create(
            group=self.context["request"].data["group"],
            title_name=self.validated_data["title_name"],
            title_description=self.validated_data["title_description"],
            rejection_reason="",
            no=self.validated_data["no"],
            status=ProjectTitle.STATUS_CHOICES.PENDING,
        )
        return new_title


class ReadProjectTitleSerializer(serializers.ModelSerializer):
    no = SerializerMethodField()
    title_name = SerializerMethodField()
    title_description = SerializerMethodField()
    status = SerializerMethodField()
    rejection_reason = SerializerMethodField()

    class Meta:
        model = ProjectTitle
        fields = ("id", "no", "title_name", "title_description", "status", "rejection_reason")

    def validate(self, data):
        return super().validate(data)

    def get_no(self, obj):
        return obj.no

    def get_title_name(self, obj):

        return obj.title_name

    def get_title_description(self, obj):
        return obj.title_description

    def get_status(self, obj):
        return obj.status

    def get_rejection_reason(self, obj):
        return obj.rejection_reason


class ReadProjectTitleFromMapSerializer(serializers.ModelSerializer):
    no = SerializerMethodField()
    title_name = SerializerMethodField()
    title_description = SerializerMethodField()
    status = SerializerMethodField()
    rejection_reason = SerializerMethodField()
    group = ReadGroupSerializer()

    class Meta:
        model = ProjectTitle
        fields = (
            "id",
            "no",
            "title_name",
            "title_description",
            "status",
            "rejection_reason",
            "group",
        )

    def id(self, obj):
        return obj["no"]

    def validate(self, data):
        return super().validate(data)

    def get_no(self, obj):
        return obj["no"]

    def get_title_name(self, obj):

        return obj["title_name"]

    def get_title_description(self, obj):
        return obj["title_description"]

    def get_status(self, obj):
        return obj["status"]

    def get_rejection_reason(self, obj):
        return obj["rejection_reason"]
